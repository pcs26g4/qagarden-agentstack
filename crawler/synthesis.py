import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("synthesis")

class DataSynthesizer:
    """
    Groups, deduplicates, and enriches crawler data for high-quality test generation.
    """
    def __init__(self, output_dir: str = "locators_consolidated"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def synthesize_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Aggregates all JSON files in a directory and synthesizes them.
        Returns a dictionary: {"path": str, "total_pages": int, "total_locators": int}
        """
        logger.info(f"Synthesizing all locators in directory: {directory_path}")
        combined_locators = {}
        combined_site_graph = {}
        base_url = "unknown"

        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # Handle both raw (list) and wrapped (dict) formats
                            raw_data = data.get("locators")
                            if raw_data is None:
                                raw_data = data.get("elements")
                            
                            locators = raw_data if raw_data is not None else {}
                            file_url = data.get("url", "unknown") if isinstance(data, dict) else "unknown"
                            
                            if isinstance(locators, list):
                                # Convert list to dict if needed for group_and_deduplicate
                                locs_dict = {}
                                for i, item in enumerate(locators):
                                    if isinstance(item, dict):
                                        if "url" not in item: item["url"] = file_url
                                        locs_dict[f"item_{i}_{file}"] = item
                                combined_locators.update(locs_dict)
                            elif isinstance(locators, dict):
                                for k, item in locators.items():
                                    if isinstance(item, dict) and "url" not in item:
                                        item["url"] = file_url
                                combined_locators.update(locators)
                            
                            if isinstance(data, dict):
                                combined_site_graph.update(data.get("site_graph", {}) or {})
                                if base_url == "unknown":
                                    base_url = data.get("config", {}).get("url", "unknown")
                    except Exception as e:
                        logger.error(f"Failed to read {file_path}: {e}")

        # Create a temporary wrapped structure for the existing synthesize method
        temp_data = {
            "locators": combined_locators,
            "site_graph": combined_site_graph,
            "config": {"url": base_url}
        }
        temp_path = os.path.join(self.output_dir, "temp_combined_raw.json")
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(temp_data, f)
        
        return self.synthesize(temp_path)

    def synthesize(self, raw_locators_path: str) -> Dict[str, Any]:
        """
        Main synthesis routine.
        Returns a dictionary: {"path": str, "total_pages": int, "total_locators": int}
        """
        logger.info(f"Starting synthesis for: {raw_locators_path}")
        
        if not os.path.exists(raw_locators_path):
            raise FileNotFoundError(f"Raw locators file not found: {raw_locators_path}")

        with open(raw_locators_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        raw_locators = data.get("locators", {})
        site_graph = data.get("site_graph", {})
        
        # 1. Grouping & Deduplication
        synthesized_locators = self._group_and_deduplicate(raw_locators)
        
        # Calculate total locators across all pages
        total_valid_locators = sum(len(locs) for locs in synthesized_locators.values())

        # 2. Enrichment
        result = {
            "site_info": {
                "base_url": data.get("config", {}).get("url", "unknown"),
                "synthesis_timestamp": datetime.now().isoformat(),
                "total_unique_pages": len(synthesized_locators),
                "total_raw_locators": len(raw_locators),
                "total_valid_locators": total_valid_locators
            },
            "pages": synthesized_locators,
            "site_graph": site_graph
        }

        # 3. Save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.output_dir, f"synthesized_{timestamp}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4)
        
        logger.info(f"Synthesis complete. Result saved to: {output_file}")
        
        return {
            "path": output_file,
            "total_pages": len(synthesized_locators),
            "total_locators": total_valid_locators,
            "raw_locators": len(raw_locators)
        }

    def _group_and_deduplicate(self, locators: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """
        Groups locators by URL and removes duplicates based on selector/hash.
        """
        grouped = {}
        for locator_id, details in locators.items():
            url = details.get("url", "unknown")
            if url not in grouped:
                grouped[url] = []
            
            # Simple deduplication by selector
            selector = details.get("selector")
            is_duplicate = any(l.get("selector") == selector for l in grouped[url])
            
            if not is_duplicate:
                # Add confidence score (v1.0: quality based on presence of stable attributes)
                details["confidence_score"] = self._calculate_confidence(details)
                grouped[url].append(details)
                
        return grouped

    def _calculate_confidence(self, locator: Dict) -> float:
        """
        Calculates a confidence score (0.0 to 1.0) based on locator quality.
        """
        score = 0.5 # Base score
        selector = locator.get("selector", "")
        
        if "id=" in selector: score += 0.3
        if "data-testid" in selector or "data-qa" in selector: score += 0.4
        if "nth-child" in selector: score -= 0.2
        if len(selector) > 200: score -= 0.1 # Too long/fragile
        
        return min(max(score, 0.1), 1.0)

if __name__ == "__main__":
    # Test stub
    import sys
    if len(sys.argv) > 1:
        syn = DataSynthesizer()
        syn.synthesize(sys.argv[1])
    else:
        logger.warning("Usage: python synthesis.py <path_to_raw_locators.json>")

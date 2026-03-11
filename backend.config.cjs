module.exports = {
  apps: [

    {
      name: "crawler-agent",
      cwd: "/home/ubuntu/qagarden-backend/crawler",
      script: "venv/bin/uvicorn",
      args: "fastapi_endpoint:app --host 0.0.0.0 --port 8005",
      interpreter: "none",
      autorestart: true,
      watch: false,
      max_memory_restart: "2G"
    },

    {
      name: "test-generator",
      cwd: "/home/ubuntu/qagarden-backend/test_generator",
      script: "/home/ubuntu/qagarden-backend/venv/bin/python",
      args: "main.py",
      interpreter: "none",
      env: {
        PORT: 8001
      }
    },

    {
      name: "playwright-gen",
      cwd: "/home/ubuntu/qagarden-backend/playwright_gen",
      script: "/home/ubuntu/qagarden-backend/venv/bin/python",
      args: "main.py",
      interpreter: "none",
      env: {
        PORT: 8002
      }
    },

    {
      name: "cicd-agent",
      cwd: "/home/ubuntu/qagarden-backend/cicd",
      script: "/home/ubuntu/qagarden-backend/venv/bin/python",
      args: "main.py",
      interpreter: "none",
      env: {
        PORT: 8003
      }
    },

    {
      name: "triage-engine",
      cwd: "/home/ubuntu/qagarden-backend/triage_engine",
      script: "/home/ubuntu/qagarden-backend/venv/bin/python",
      args: "main.py",
      interpreter: "none",
      env: {
        PORT: 8004
      }
    }

  ]
};
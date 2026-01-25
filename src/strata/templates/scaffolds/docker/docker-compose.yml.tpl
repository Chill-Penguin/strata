services:
  # @include base_service_template
  # @vars
  #   service_name: cadence-api
  #   context: ./backend
  #   container_name: cadence-api
  #   command: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --log-level debug --proxy-headers --forwarded-allow-ips=*
  #   volumes:
  #     - ./backend:/app/backend
  #     - /lily/notes:/app/notes
  #   traefik_port: 8000
  #   homepage_group: Productivity
  #   homepage_name: cadence-api
  #   homepage_icon: None
  #   homepage_description: Task Notification Service

  # @include base_service_template
  # @vars
  #   service_name: cadence
  #   context: .
  #   dockerfile: frontend/Dockerfile
  #   container_name: cadence
  #   depends_on: cadence-api
  #   traefik_port: 80
  #   homepage_group: Productivity
  #   homepage_name: cadence
  #   homepage_icon: None
  #   homepage_description: Task Notification Service

  # @include base_service_template
  # @vars
  #   service_name: migrate
  #   context: ./backend
  #   command: alembic upgrade head
  #   volumes:
  #     - ./:/app
  #   restart_policy: no

  # @include base_service_template
  # @vars
  #   service_name: rq-worker-jobs
  #   context: ./backend
  #   command: python -m backend.services.rq.worker jobs
  #   volumes:
  #     - .:/app
  #   depends_on: cadence-api

  # @include base_service_template
  # @vars
  #   service_name: rq-worker-notifications
  #   context: ./backend
  #   command: python -m backend.services.rq.worker notifications
  #   volumes:
  #     - .:/app
  #   depends_on: cadence-api

  # @include base_service_template
  # @vars
  #   service_name: rq-cron
  #   context: ./backend
  #   command: rq cron backend.services.rq.cron
  #   working_dir: /app
  #   environment:
  #     - PYTHONPATH=/app
  #   volumes:
  #     - .:/app
  #   depends_on: cadence-api

# @include base_traefik_network_template

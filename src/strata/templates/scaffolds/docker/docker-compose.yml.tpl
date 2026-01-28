services:
  # @include base_service_template
  # @vars
  #   service_name: cadence-api
  #   context: ./backend
  #   container_name: cadence-api
  #   command: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --log-level debug --proxy-headers --forwarded-allow-ips=*
  #   volumes:
  #     - ./backend:/app/backend
  #   traefik_port: 8000


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


# @include base_traefik_network_template

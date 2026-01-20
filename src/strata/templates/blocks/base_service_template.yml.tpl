{{ service_name }}:
  {% if image | default(false) %}
  image: {{ image }}:{{ image_tag | default('latest') }}
  {% endif %}

  {% if ports | default(false) %}
  {% endif %}

  {% if context | default(false) %}
  build:
    context: {{ context }}
    {% if dockerfile | default(false) %}
    dockerfile: {{ dockerfile }}
    {% endif %}
  {% endif %}

  {% if container_name | default(false) %}
  container_name: {{ container_name }}
  {% endif %}

  {% if command | default(false) %}
  command: {{ command }}
  {% endif %}

  {% if working_dir | default(false) %}
  working_dir: {{ working_dir }}
  {% endif %}

  {% if volumes | default(false) %}
  volumes:
  {% for vol in volumes %}
    - {{ vol }}
  {% endfor %}
  {% endif %}

    {% if environment | default(false) %}
  environment:
  {% for e in environment %}
    - {{ e }}
  {% endfor %}
  {% endif %}

  {% if depends_on | default(false) %}
  depends_on:
    - {{ depends_on }}
  {% endif %}

  env_file:
    - .env-prod

  restart: {{ restart_policy | default('no') }}

  {% set has_labels = (traefik_port | default(false)) or (homepage_group | default(false)) %}
  {% if has_labels %}
  labels:
    {% if traefik_port | default(false) %}
    # @include traefik_labels_template
    {% endif %}

    {% if homepage_group | default(false) %}
    # @include homepage_labels_template

    {% endif %}
  {% endif %}

  {% if timezone | default(false) %}
  # @include base_environment_template

  {% endif %}

  networks:
    - traefik

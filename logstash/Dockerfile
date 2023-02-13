# https://www.docker.elastic.co/
FROM docker.elastic.co/logstash/logstash:${ELASTIC_VERSION}

RUN logstash-plugin install logstash-input-mongodb
# Add your logstash plugins setup here
# Example: RUN logstash-plugin install logstash-filter-json

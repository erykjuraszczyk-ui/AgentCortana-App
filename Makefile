.PHONY: up rebuild logs ps down sse health

up:        ## start w tle
\tdocker compose up -d
rebuild:   ## przebudowa + start
\tdocker compose up -d --build
logs:      ## logi aplikacji
\tdocker logs -f cortana-app
ps:        ## status usług
\tdocker compose ps
down:      ## zatrzymaj
\tdocker compose down
sse:       ## start z EXPERIMENTAL_ACT_STREAM=1
\tEXPERIMENTAL_ACT_STREAM=1 docker compose up -d --build
health:    ## szybki check
\tcurl -i http://127.0.0.1:8000/health

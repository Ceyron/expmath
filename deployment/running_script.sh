nohup bokeh serve /var/www/expmath/plots/*.py \
    --port 9001 \
    --address=0.0.0.0 \
    --allow-websocket-origin=*:9001 \
    --allow-websocket-origin=*:8080 \
    --allow-websocket-origin=*:80 &

apachectl -D FOREGROUND

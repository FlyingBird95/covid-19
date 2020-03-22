compile: ./bin/run_cloud_sql_proxy/compile
release: flask db upgrade
web: gunicorn covid19.app:create_app\(\) -b 0.0.0.0:$PORT -w 3

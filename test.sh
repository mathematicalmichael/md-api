curl --request POST \
    --url http://0.0.0.0:8000/convert \
    --header 'Content-Type: application/json' \
    --data '{
        "content": "https://wikipedia.org"
    }'
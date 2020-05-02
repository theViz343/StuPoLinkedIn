#! /bin/bash
echo "Please wait...."
python3 -m venv venv1
source venv1/bin/activate
pip3 freeze > requirements.txt
deactivate
cat <<EOF > config.json
{
"client_id" : "your_client_id_here",
"client_secret" : "your_client_secret_here"
}
EOF

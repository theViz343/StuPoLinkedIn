#! /bin/bash
echo "Please wait...."
python3 -m venv venv1
source venv1/bin/activate
pip3 install django
pip3 install urllib3
pip3 install requests
deactivate
cat <<EOF > config.json
{
"client_id" : "your_client_id_here",
"client_secret" : "your_client_secret_here",
}
EOF

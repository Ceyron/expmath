echo "INFO: Stopping expmath. This could take some time. Docker will confirm with the hash."
container_id=$(sudo docker ps | grep expmath | cut -d " " -f1)
sudo docker stop ${container_id}

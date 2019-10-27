# Get the id of the previous expmath image so that it can be deleted later on
line=$(sudo docker images | grep expmath)
old_id=$(echo $line | cut -d " " -f3)

# Build image
sudo docker build -t expmath .

# Delete old image only if building the new one was successfully
if [[$? -e 0 ]]
then
    sudo docker image rm ${old_id}
fi

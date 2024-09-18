#!/bin/zsh

# > magi-upload <port> <username> /src /dest

# You may need to setup SSH keys on the login.khoury.northeastern
# You may need to enable remote login under System Settings
# Please do _NOT_ setup SSH keys on shared Magi computers

echo "connecting to Khoury servers"
ssh -NL $1:Magi-03:22 $2@login.khoury.northeastern.edu &
pid=$!
sleep 1
echo "forwarding on port $1"
sleep 1
echo "uploading from: '$3'"
echo "uploading to: '$4'"
scp -rP $1 $3 viteklab@localhost:$4
kill $pid
echo "closing connection to server"

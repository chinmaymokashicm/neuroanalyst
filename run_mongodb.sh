# apptainer run \
#     -B $HOME/mongodb/data:/data/db \
#     -B $HOME/mongodb/logs:/var/log/mongodb \
#     mongo_latest.sif --noauth --bind_ip_all \
#     --fork --logpath mongo_logs.log

# apptainer exec mongo_latest.sif mongod --config mongod.conf


# ! Do not run this script - this is only for reading


screen -S mongo_apptainer
# rm $HOME/data/mongodb/WiredTiger.lock
# rm $HOME/data/mongodb/WiredTiger*
# rm $HOME/data/mongodb/mongod.lock
cd $HOME/apptainer_images/mongodb
apptainer run \
    -B $HOME/data/mongodb:/data/db \
    -B $HOME/logs/mongodb:/var/log/mongodb \
    mongo_latest.sif

# apptainer run --writable \
#     -B $HOME/data/mongodb:/data/db \
#     -B $HOME/logs/mongodb:/var/log/mongodb \
#     mongo_latest.sif \
#     mongod --repair --dbpath /data/db
    
# cd $HOME/apptainer_images/mongodb
# apptainer instance start \
#     -B $HOME/data/mongodb:/data/db \
#     -B $HOME/logs/mongodb:/var/log/mongodb \
#     mongo_latest.sif mongo_latest

# Aqua_Green_DataWareHouse

## Architecture Overview
<img width="1313" alt="Screenshot 2025-01-27 at 9 09 32 in the morning" src="https://github.com/user-attachments/assets/6b3b8e14-6449-461b-acd7-4750fa4643f3" />

## Set up Zookeeper, Kafka Cluster, and CMAK (Cluster Manager Apache Kafka)
https://www.youtube.com/watch?v=F6PUQ3k6zmg&t=1880s

## Commands to run
### Kafka Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

### Kafka Cluster
JMX_PORT=8004 bin/kafka-server-start.sh config/server.properties

### CMAK
bin/cmak -Dconfig.file=conf/application.conf -Dhttp.port=8080 \
-J--add-opens=java.base/sun.net.www.protocol.file=ALL-UNNAMED \
-J--add-exports=java.base/sun.net.www.protocol.file=ALL-UNNAMED

<img width="806" alt="Screenshot 2025-01-27 at 9 12 35 in the morning" src="https://github.com/user-attachments/assets/b0aef37b-261c-46a3-bf15-8cf57b7f5470" />

### Producer 
1. Cd to Kafka Connection Directory
2. Activate Python Environment: source kafka-env1/bin/activate
3. Command to run: python producer.python

### Consumer
1. Cd to Kafka Connection Directory
2. Activate Python Environment: source kafka-env1/bin/activate
3. Command to run: python consumer.python   

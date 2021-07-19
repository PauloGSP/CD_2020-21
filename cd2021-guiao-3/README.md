## Tests:

run `pytest`


## Diagram:

```https://www.websequencediagrams.com
title Message Broker

note left of Consumer: Connection estabilished
Consumer->Broker: Announce Serialization Mechanism

note left of Consumer: Can subscribe to topics any time

Consumer->Broker: Subscribe to topic X
Broker->Consumer: Send Last saved message in X

note right of Broker: List just the topic names

Consumer->Broker: Request list of all topics
Broker->Consumer: Response list of all topics

note left of Producer: Connection estabilished

Producer -> Broker: Announce Serialization Mechanism
Producer -> Broker: Publish message to topic X

Broker ->Consumer: Send message to consumer
Consumer -> Broker: Cancel topic X subscription

Producer -> Broker: Publish message to topic X
note left of Consumer: Doesn't receive last message
```




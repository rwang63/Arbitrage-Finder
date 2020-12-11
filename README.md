This program allows the user to connect with a publisher as a subscriber and continuously receive UDP datagrams. These datagrams contain currency conversion quotes. 
Using these quotes, we store them in a graph and run Bellman-Ford at each update to check if there is an arbitrage opportunity.
An arbitrage opportunity is defined as converting currencies and ending up at the original currency with more money than you started with. 
If an arbitrage opportunity presents itself, it is reported, otherwise messages are continuously received from the publisher.

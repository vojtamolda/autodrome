
# Autodrome




## Building


```bash
brew install cmake zeromq capnp
pip install -r requirements.txt -r requirements-darwin.txt

mkdir "simulator/plugin/build" && cd "simulator/plugin/build"
cmake .. && make && make install
```


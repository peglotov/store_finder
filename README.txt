The solution contains the following steps:
    * parse command line arguments;
    * load csv data from store locations file;
    * call locationiq.org api to get lat, lon of input address/zip;
    * scan through store locations to find the closest location;
        - this can be costly if number of entities is large; in such cases a special data structure can be used to store locations (kd-tree, etc.);
        - distance is computed using geopy.distance module;
    * output result, taking into account distance units and output format;
    * usage examples:
        ./find_store.py --address="1200 Market St., San Francisco, CA"
        ./find_store.py --address="1200 Market St., San Francisco, CA" --units=km
    * testing:
        python ./tests.py

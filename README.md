# Seismic Phase Array Match Maker 

SPAM creates heat maps for where on earth is the best place to go 'hunting' for seismic phases. In addition, it can act as an array former. 

## Check for dependencies and create environment
```
cd spam
python -m venv .venv
source .venv/bin/activate
python pip install -v -e .
```


test example:
```
cd example
spamcalc -s 201511260545.stations -e 201511260545.event --minsta 1 --mineq 1 --phase SKKS
```

Command Structure 
```
spamcalc -s stationfilename -e eqcatalogfilename --minsta 1 --mineq 1 --phase SKKS
```

required inputs:  
'-p', '--phases', phase(s) of interest  
'-s', '--stations', stationfile name  
'-e', '--earthquakes' earthquake catalog name  
'--minsta', type=int, default=1, min number of stations near a grid point to form an array  
'--mineq', type=int, default=1, min number of earthquakes at an array to be successful  

optional inputs:  
'--grid', type=int, default=40000, number of grid points over earth  
'--region', type=int, nargs=4, restrict grid points to WESN box  
'--arrayradius', type=float, default=1.0, radius of array in degrees  
'-o', '--outfile', default="spam.jsn", output file  

Station List:
If you already have sac files for an earthquake you can use creatSTA.py in prep_scripts

Event List:
If you don't have an event list an example for creating one is given in prep_scripts

-----------------------
## Some Notes 


grid spacing:
we use the fibanocci lattice for evenly (as much as possible) spaced grid points. for a chart on number of points and grid spacing please refer to the resources folder. would also like to add a photo of this information here but i dont know how to do that yet so please just look at the grid spacing folder


| No. of Points | Degree Spacing |
|   1000 | 3.623703272 |
|   1500 | 2.958741331 |
|   2000 | 2.562345156 |
|   2500 | 2.291831181 |
|   3000 | 2.092146059 |
|   3500 | 1.936950873 |
|   4000 | 1.811851636 |
|   4500 | 1.708230104 |
|   5000 | 1.620569369 |
|   5500 | 1.545152267 |
|   6000 | 1.479370666 |
|   6500 | 1.421333361 |
|   8000 | 1.28117 |
|   9000 | 1.2079 |
|   20000 | 0.81028 |
|   30000 | 0.66159467 |
|   40000 | 0.572957795 |
|   50000 | 0.512469 |
|   60000| 0.467818 |



array configriation, array radius:
1 degree at the poles looks different than 1 degree at the equator. it is recommend that the array radius is 2-2.5 times the grid spacing to ensure proper sampling. this will also ensure that the grid point used to form the array is the best possible grid point in the suite to represent the array. we are currently working on improving array configuartion and deleting duplicates by looking at sapital distribution and density of stations in an array.


Please email me with any questions: amuhly@email.sc.edu 

----------------------
## Array Specific Information
to prepare files for array processing:  

prepvespa  
- returns a list of grid points, stations, basestations, and eq catalog  
-----------------------
## Version Information
version 0.0.1Beta - original version that is not compatible with Ubuntu 26.04 LT

version 0.0.2Beta - updated version compatible with Ubuntu 26.04 LT by using @classmethod to create   json readable objects and dictionaries

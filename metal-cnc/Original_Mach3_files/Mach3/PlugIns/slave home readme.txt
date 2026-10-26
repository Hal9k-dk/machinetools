if you want to refer home with slave at the same time.
1. please set the home slave with master in the general logic configure in mach3
2. please set the home slave pin in the input signals in ports and pins.such as A home pin nunmber and enabled should be setted ok.
3. please modify the home macro with refcombination(9) .x is 1,y is 2,z is 4,a is 8.
 refcombination(9) is x and slave a home together.
4. please disable home pin as limit in the ncpod plugin windows

if any problem please visit our web :www.cdxhctech.com
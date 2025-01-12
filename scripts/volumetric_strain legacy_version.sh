#!/bin/bash

#Bash script for 2D strain
#for every strain in x direction, y strains in y direction 
#Put your INCAR, POTCAR, KPOINTS, Submission file in the same folder with 2D_strain.sh
#use fractional coordinate in the POSCAR file to apply strains on atoms defined in terms of lattice vector
#run this file

EXX=0      #e1 strain
EYY=0      #e2 strain
EZZ=0      #e3 strain
EYZ=0      #ezy or eyz or e4 strain
EXZ=0      #exz or ezx or e5 strain
EXY=0      #exy or eyx or e6 strain

A=(4.8049445594525109    0.0000000000000000    0.0000000000000000)  #1st lattice vector
B=( -0.0000000000000000    4.9416045518304639    0.0000000000000000)  #2nd lattice vector
C=(0.0000000000000000    0.0000000000000000    7.0241627070936206)  #3rd lattice vector

# Strain range in XX direction
for EXX in $(seq -0.05 0.01 0.05)
do 
mkdir strain_XX_$EXX
cd strain_XX_$EXX 
  # Strain range in YY direction
  for EYY in $(seq -0.05 0.01 0.05)
  do   
  mkdir strain_YY_$EYY
  cd strain_YY_$EYY  
        # Strain range in ZZ direction
        for EZZ in $(seq -0.05 0.01 0.05)
        do  
cat <<EOF >POSCAR
   Al  O                                      
1.0000000000000000
$(echo "(${A[0]}*(1+$EXX))+(${A[1]}*($EXY/2))+(${A[2]}*($EXZ/2))" | bc)   $(echo "(${A[0]}*($EXY/2))+(${A[1]}*(1+$EYY))+(${A[2]}*($EYZ/2))" | bc)    $(echo "(${A[0]}*($EXZ/2))+(${A[1]}*($EYZ/2))+(${A[2]}*(1+$EZZ))" | bc)               
$(echo "(${B[0]}*(1+$EXX))+(${B[1]}*($EXY/2))+(${B[2]}*($EXZ/2))" | bc)   $(echo "(${B[0]}*($EXY/2))+(${B[1]}*(1+$EYY))+(${B[2]}*($EYZ/2))" | bc)    $(echo "(${B[0]}*($EXZ/2))+(${B[1]}*($EYZ/2))+(${B[2]}*(1+$EZZ))" | bc)                             
$(echo "(${C[0]}*(1+$EXX))+(${C[1]}*($EXY/2))+(${C[2]}*($EXZ/2))" | bc)   $(echo "(${C[0]}*($EXY/2))+(${C[1]}*(1+$EYY))+(${C[2]}*($EYZ/2))" | bc)    $(echo "(${C[0]}*($EXZ/2))+(${C[1]}*($EYZ/2))+(${C[2]}*(1+$EZZ))" | bc)                                                                                  
   Al   O 
     8    12
Selective dynamics
Direct
  0.2523002353554037  0.0313963657290514  0.3899885770513160   T   T   T
  0.2523002353554037  0.4686036324055040  0.6100114229768929   T   T   T
  0.2476997646445963  0.5313963676747305  0.1100114080825527   T   T   T
  0.2476997646445963  0.9686036323453281  0.8899885769948985   T   T   T
  0.7476997349350850  0.9686036323453281  0.6100114229768929   T   T   T
  0.7476997349350850  0.5313963676747305  0.3899885770513160   T   T   T
  0.7523002650649150  0.4686036324055040  0.8899885769948985   T   T   T
  0.7523002650649150  0.0313963657290514  0.1100114080825527   T   T   T
  0.1070727541729076  0.1023897509358228  0.6541476566137407   T   T   T
  0.1070727541729076  0.3976102415823399  0.3458523434144675   T   T   T
  0.3929272383997110  0.6023897286106482  0.8458523433580507   T   T   T
  0.3929272383997110  0.8976102714094104  0.1541476417194010   T   T   T
  0.8929272683155354  0.8976102714094104  0.3458523434144675   T   T   T
  0.8929272683155354  0.6023897286106482  0.6541476566137407   T   T   T
  0.6070727316844646  0.3976102415823399  0.1541476417194010   T   T   T
  0.6070727316844646  0.1023897509358228  0.8458523433580507   T   T   T
  0.0501883691512118  0.2500000000702016  0.0000000000000000   T   T   T
  0.4498116347687957  0.7500000000100329  0.4999999999435829   T   T   T
  0.9498116048529711  0.7500000000100329  0.0000000000000000   T   T   T
  0.5501883951470289  0.2500000000702016  0.4999999999435829   T   T   T
EOF
	mkdir strain_ZZ_$EZZ
	cp ../../INCAR strain_ZZ_$EZZ/
	cp POSCAR strain_ZZ_$EZZ/
	cp ../../POTCAR strain_ZZ_$EZZ/
	cp ../../KPOINTS strain_ZZ_$EZZ/
	cp ../../vasp_jobsub.sh strain_ZZ_$EZZ/
	cd strain_ZZ_$EZZ

	#submission
	#qsub VASP_JobSub.sh
	# post process 
	#E=`grep 'F' OSZICAR|tail -n 1 | awk '{ print $5}'`;
	#echo $EXX $E >>../pos-conv.txt
	cd ../
	done
  cd ../	
  done	
cd ..
done


#Crystal lattice vectors (in cartesian axis):     x or a  y or b  z or c
 #1st lattice vector   a(1)    a(2)   a(3)
 #2nd lattice vector   b(1)    b(2)   b(3)
 #3rd lattice vector   c(1)    c(2)   c(3)
#Hexagonal --- celldm(3)=c/ l_c
#a = l_c*(1,0,0),  b =  l_c*(-1/2,sqrt(3)/2,0),  c =  l_c*(0,0,c/l_c)
# The strain tensor ϵ is defined by
#  ϵ = [ ϵ1      ϵ6/2   ϵ5/2    
#        ϵ6/2    ϵ2     ϵ4/2     
#        ϵ5/2    ϵ4/2   ϵ3 ]



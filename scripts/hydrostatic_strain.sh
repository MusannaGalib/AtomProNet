#!/bin/bash

#Bash script for hydrostatic strain
#for every strain in x direction, y strains in y direction 
#Put your INCAR, POTCAR, KPOINTS, POSCAR, Submission file in the same folder with hydrostatic_strain.sh
#use fractional coordinate in the POSCAR file to apply strains on atoms defined in terms of lattice vector
#run this file

EXX=0      #e1 strain
EYY=0      #e2 strain
EZZ=0      #e3 strain
EYZ=0      #ezy or eyz or e4 strain
EXZ=0      #exz or ezx or e5 strain
EXY=0      #exy or eyx or e6 strain


# Extract lattice vectors from POSCAR
POSCAR_FILE="./POSCAR"
if [[ -f "$POSCAR_FILE" ]]; then
    header=$(sed -n '1p' "$POSCAR_FILE")              # First line: header
    scale=$(sed -n '2p' "$POSCAR_FILE")               # Second line: scaling factor
    A=($(sed -n '3p' "$POSCAR_FILE"))                 # Third line: first lattice vector
    B=($(sed -n '4p' "$POSCAR_FILE"))                 # Fourth line: second lattice vector
    C=($(sed -n '5p' "$POSCAR_FILE"))                 # Fifth line: third lattice vector
    atom_types=$(sed -n '6p' "$POSCAR_FILE")          # Sixth line: atom types
    atom_counts=$(sed -n '7p' "$POSCAR_FILE")         # Seventh line: atom counts
    coord_type=$(sed -n '8p' "$POSCAR_FILE")          # Eighth line: coordinate type (Direct/Cartesian)
    coordinates=$(sed -n '9,$p' "$POSCAR_FILE")       # Remaining lines: atomic coordinates
else
    echo "Error: POSCAR file not found in the current directory."
    exit 1
fi



# Initialize counter
counter=0


# Strain range in XX direction
for EXX in $(seq -0.05 0.01 0.05)
do 
((counter++))
mkdir strain_XX_$EXX
cd strain_XX_$EXX 
  # Strain range in YY direction  
  mkdir strain_YY_$EXX
  cd strain_YY_$EXX  
  # Strain range in ZZ direction 
  EYY=$EXX
  EZZ=$EXX
  echo "Debug: Simulation $counter - EXX=$EXX, EYY=$EYY, EZZ=$EZZ"   
cat <<EOF >POSCAR
$header
$scale
$(echo "(${A[0]}*(1+$EXX))+(${A[1]}*($EXY/2))+(${A[2]}*($EXZ/2))" | bc)   $(echo "(${A[0]}*($EXY/2))+(${A[1]}*(1+$EYY))+(${A[2]}*($EYZ/2))" | bc)    $(echo "(${A[0]}*($EXZ/2))+(${A[1]}*($EYZ/2))+(${A[2]}*(1+$EZZ))" | bc)
$(echo "(${B[0]}*(1+$EXX))+(${B[1]}*($EXY/2))+(${B[2]}*($EXZ/2))" | bc)   $(echo "(${B[0]}*($EXY/2))+(${B[1]}*(1+$EYY))+(${B[2]}*($EYZ/2))" | bc)    $(echo "(${B[0]}*($EXZ/2))+(${B[1]}*($EYZ/2))+(${B[2]}*(1+$EZZ))" | bc)
$(echo "(${C[0]}*(1+$EXX))+(${C[1]}*($EXY/2))+(${C[2]}*($EXZ/2))" | bc)   $(echo "(${C[0]}*($EXY/2))+(${C[1]}*(1+$EYY))+(${C[2]}*($EYZ/2))" | bc)    $(echo "(${C[0]}*($EXZ/2))+(${C[1]}*($EYZ/2))+(${C[2]}*(1+$EZZ))" | bc)
$atom_types
$atom_counts
$coord_type
$coordinates
EOF
	mkdir strain_ZZ_$EXX
	cp ../../INCAR strain_ZZ_$EXX/
	cp POSCAR strain_ZZ_$EXX/
	cp ../../POTCAR strain_ZZ_$EXX/
	cp ../../KPOINTS strain_ZZ_$EXX/
	cp ../../vasp_jobsub.sh strain_ZZ_$EXX/
	cd strain_ZZ_$EXX

	#submission
	#qsub VASP_JobSub.sh
	# post process 
	#E=`grep 'F' OSZICAR|tail -n 1 | awk '{ print $5}'`;
	#echo $EXX $E >>../pos-conv.txt
	cd ../
	
  cd ../	
  	
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



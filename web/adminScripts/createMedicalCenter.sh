#!/bin/bash
# This script will create a new Medical Center
echo
echo
echo "Hello there, you are going to create a new Medical Center..."
echo
echo -e "Enter the \033[31mname\033[0m of the medical center (e.g., Addenbrookes) and press [ENTER]: "
read name
echo
echo -e "Enter the 2-characters \033[31minternal name\033[0m of the medical center  (e.g., AB) and press [ENTER]: "
read internalName
echo


~/.virtualenvs/venvdj1.4/bin/python -c "import utils1_4; utils1_4.createSource('$name', 'Hospital', '$internalName')"
echo
~/.virtualenvs/venvdj1.7/bin/python -c "import utils1_7; utils1_7.createInstitution('$name', 'Medical Center', '$internalName')"

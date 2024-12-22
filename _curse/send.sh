cd /home/aleh/7-term/_curse
tar -cvf diploma.tar --exclude='.venv' --exclude='*/__pycache__' --exclude='node_modules' diploma
scp diploma.tar aleh@ugabuntu:/home/aleh/diploma/diploma.tar

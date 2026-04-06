# ph360_activity_2026

This is the repository for the PUB_HLTH Seminar in Data Science - Week 2 activity. The two-part assignment focuses on linking two datasets following good software engineering practices. For the first part, you will be asked to implement a data linkage method of your choice to sufficiently link the two datasets provided. You may use any of the data linkage methods introduced in lecture, but feel free to research and apply alternative techniques if there are any that pique your interest. The second part will ask you to conduct a code review of a classmate’s pull request.  

## Part I.  Data Linkage (Due 4/13) 

1. Clone this repository. 
2. Checkout a branch from ‘main’ and name it ‘{Initial}_dev’. Create a file called ‘{Initial}_algo.R / .Rmd / .py / .ipynb’. Choose whichever format you are most comfortable with.  
3. Implement a data linkage method of your choice. You may use as many or as little columns as you deem appropriate, but please do NOT use the ‘UUID’ field, as this is the ground truth (and using this is cheating!). UUID stands for Universal Unique Identifier. It is a 128-bit, 36-char alphanumeric string. 
4. Report accuracy, precision, and recall of your algorithm using the ‘UUID’ field.  
5. Push your work to your remote branch with a commit message. 
6. Create a pull request (PR) and add your assigned reviewer. 

## Part II. Code Review (Due 4/20) 

1. Conduct a thoughtful code review of your partner’s pull request. 
2. Approve PR once comments are addressed. 
3. Address comments from the code review you received. 
4. Merge PR to ‘main’ once approved. 

NOTE. It is unlikely you will see merge conflicts since you are all working on different files. However, if you do see merge conflicts and are not sure how to resolve them, please don’t hesitate to reach out. It is good practice to periodically pull from main to ensure you are working with the most recent version of ‘main’ and do not accidentally overwrite someone else’s merged changes.

## Datasets
Two datasets are located in the `data/` folder. Note that they have a 90% match rate, so not all members of each file exist in the other. The datasets also contain some intentional noise, so exploration and preprocessing before any method implementation will be helpful.

## Author
Da In Lee (@diane-lee-01)
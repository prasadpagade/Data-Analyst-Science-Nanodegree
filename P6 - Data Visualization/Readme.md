## Data Visualization: Titanic Passenger Survival 
by Prasad Pagade, in fulfillment of Udacity's [Data Analyst Nanodegree](https://www.udacity.com/course/nd002), Project 6

### Summary

This project shows 3 different bar graphs. It shows percentage of survival for each gender, passengers travelling with family and location from where the passengers embarked the ship by passenger class. 
This dashboard helps reader understand what factors helped a passenger survive the fateful crash.

### Design

#### Exploratory Data Analysis and Cleaning (Python)

I downloaded the data from [Kaggle - Machine Learning from Disaster](https://www.kaggle.com/c/titanic/data), 
which was already clean and didn't need extensive data wrangling or transformation.
I used techniques learnt in P2: Investigate a dataset with **Python** and came up with few initial hypothesis. 
While exploring the data, I cleaned up some data like missing ages and embarked locations. I mapped the columns **Pclass** (1:Upper Class, 2: Middle Class, 3: Lower Class)
and **Embarked** (S:Southampton, C:Cherbourg, Q:Queenstown)
with more readable names so that it can be used directly in the charts later. 

I created a new column **person** from the column Sex and Age so that we had three types of classification - Male, Female or Child(child is a person who is 15 years old or less). I saved this modified
file as "titanic_data_modified.csv"

#### Data Visualization (dimple.js)

I decided to use **dimple.js** to produce the stacked bar chart and used **d3.js** objects to manipulate the html elements.

I considered using multiple chart types to test which one represents the findings most convincingly.
I re-evaluated different chart type by tweaking few line of code and confirm my initial assumption, 
a bar chart is sufficient to display data. 

#### Initial Design decisions

My initial designs included a stacked bar graph by gender. I wanted to include more graphs and animation from this point forward.

This initial iteration can be viewed at `index_old.html`, below are the screenshots few iterations of the graph:

![First Chart](https://github.com/prasadpagade/Data-Analyst-Science-Nanodegree/blob/master/P6%20-%20Data%20Visualization/Images/intial_v1.png)

![Second Chart](https://github.com/prasadpagade/Data-Analyst-Science-Nanodegree/blob/master/P6%20-%20Data%20Visualization/Images/legends.png)

![Second Chart](https://github.com/prasadpagade/Data-Analyst-Science-Nanodegree/blob/master/P6%20-%20Data%20Visualization/Images/legends.png)

![Third Chart](https://github.com/prasadpagade/Data-Analyst-Science-Nanodegree/blob/master/P6%20-%20Data%20Visualization/Images/Fixing_buttons_position.png)

### Feedback

I gathered feedback from 3 different people and made iterations to my design:

#### Feedback #1

> Great Visualisation.The graph conveys the message. it be easy for people to understand better,
if we have a survival rate/percentage instead of people survived

#### Feedback #2

> I think it is really good. It is "clean" and easily understood.
While it is fine as it is, as we interact, the new category legends are added, but the old legends are not removed. I don't know how much work that is to correct.

#### Feedback #3

> The button position is wierd. On minimizing it overlaps on the chart. I would suggest fixing the button elements so that they donot overlap on the chart.

### Post-feedback Design

I implemented the following changes:

- Reduced the widths of the bar charts. So they look a lot cleaner.
- Increased the font size of the legends and the axes.
- Changed the Y-axis to percentage scale.
- Fixed the button overlapping problem.
- Fixed the legend clearing problem so that only the legends for the selected charts appear.
- Added interactive text display which imparts user with information on each graph.

Final version of the data visualization is shown below:

![Final Chart](https://github.com/prasadpagade/Data-Analyst-Science-Nanodegree/blob/master/P6%20-%20Data%20Visualization/Images/final_version.PNG)

[Link to the Visualization](http://bl.ocks.org/prasadpagade/raw/00afd74899b680f25ce27a7c6a8aacc7/)

### Resources

- [dimple.js Documentation](http://dimplejs.org/)
- [Data Visualization and D3.js (Udacity)](https://www.udacity.com/course/viewer#!/c-ud507-nd)

### Data

- `titanic_data_modified.csv`: original downloaded dataset with minor cleaning.

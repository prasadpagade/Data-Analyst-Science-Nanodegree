getwd()

setwd('C:/Users/PrasadPagade/Downloads')
getwd()

statesInfo <- read.csv('stateData.csv')

subset(statesInfo, state.region == 1)

subset(statesInfo, illiteracy == 0.5)

statesInfo[statesInfo$illiteracy == 0.5,]

```{r}
summary(mtcars)
```

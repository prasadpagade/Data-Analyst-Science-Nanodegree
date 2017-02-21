udacious <- c("Chris Saden", "Lauren Castellano",
              "Sarah Spikes","Dean Eckles",
              "Andy Brown", "Moira Burke",
              "Kunal Chawla")

numbers <- c(1:10)

numbers
numbers <- c(numbers, 11:20)
numbers

udacious <- c("Chris Saden", "Lauren Castellano",
              "Sarah Spikes","Dean Eckles",
              "Andy Brown", "Moira Burke",
              "Kunal Chawla", "Prasad Pagade")

mystery = nchar(udacious)
mystery

mystery == 11

udacious[mystery == 11]

data(mtcars)

names(mtcars)

?mtcars

mtcars

str(mtcars)

dim(mtcars)

?row.names

row.names(mtcars) <- c(1:32)

mtcars

data(mtcars)
head(mtcars, 10)

names(mtcars)
mtcars$am

mean(mtcars$mpg)

rm(list=ls())
library(ggplot2)

d <- readRDS('waarnemingen_occurrences_clean.RDS')
anyNA(d$species)
anyNA(d$occurences)

#order data set by number of occurrence records and add abundance rank column
d <- d[order(d$occurences, decreasing=TRUE),]
d$abundance_rank <- 1:nrow(d)

hist(log10(d$occurences), breaks=20)
qqnorm(y=log10(d$occurences))

#fit a geometric series model for the rank abundance curve

mod1 <- lm( log10(occurences) ~ abundance_rank, data=d)
summary(mod1)
plot(mod1) #fit is not so good
predictions1 <- predict(mod1, abundance_rank= 1:nrow(d))

#try cutting off tails of rare and common species and refitting
dt <- d[100:350,]
mod2 <- lm( log10(occurences) ~ abundance_rank, data=dt)
summary(mod2)
plot(mod2) #fit is better for this range in the data
simdat <- data.frame(abundance_rank= 1:nrow(d))
predictions2 <- predict(mod2, simdat)
coefs <- coefficients(mod2)

#create a step plot for log10abundance vs. abundance rank
ggplot(data=d, aes(x=abundance_rank, y=occurences))+
  geom_step(lwd=0.5)+
  geom_line(aes(y=10^predictions2, x=1:nrow(d)), lwd=0.5, lty=2, col='red')+
  xlab('species abundance rank')+
  ylab('log10(species abundance)')+
  annotate(geom='text',col='red',x=350,y=100000,label='log10(species abundance) =')+
  annotate(geom='text',col='red',x=350,y=40000,label='5.71 - 0.0105 x species rank')+
  scale_y_log10(guide='axis_logticks', breaks=c(1,1e1,1e2,1e3,1e4,1e5), labels=c('1','10','100','1,000','10,000','100,000'))+
  theme_bw()


#compute the Shannon information for each species in the dataset
N <- sum(d$occurences)
d$shannon_info <- log2(N) - log2(d$occurences)
hist(d$shannon_info, breaks=20)
p_vec <- 2^(-d$shannon_info)*d$shannon_info 
sum(p_vec)/log2(448) #80% of the theoretical maximum entropy distribution (ie discrete uniform)

write.csv(d, file='ranked_species_waarnemingen.csv', row.names=FALSE)




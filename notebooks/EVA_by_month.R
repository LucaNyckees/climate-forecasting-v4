setwd("~/Documents/SCV/SCV_project3/notebooks")

library(evd)
library(ismev)
library(stats)
library(nlme)
library(POT)


period = 365.25

#--- Max temperature data processing
df_max <- read.delim("../data/observatoire-geneve/TX_STAID000241.txt", header = FALSE, sep=",", skip=20)
colnames(df_max) <- c("SOUID", "date", "TG", "Q_TG")
df_max <- df_max[df_max$Q_TG != '9' ,]
df_max$TG<-df_max$TG/10
df_max$index <-  seq(from = 1, to = length(df_max$TG),by = 1)
df_max<- subset(df_max, select=-c(SOUID,Q_TG))
df_max$date <- as.Date(as.character(df_max$date), "%Y%m%d")

df_max$Year <- format(as.Date(df_max$date, format="%Y/%m/%d"),"%Y")
df_max$Month <- format(as.Date(df_max$date, format="%Y/%m/%d"),"%m")
df_max$Day <- format(as.Date(df_max$date, format="%Y/%m/%d"),"%d")

month <- unique(df_max$Month)

## ---- POT approach --- ##

## --- Mean residual life plots

for(i in 1:12){
  dat <- subset(df_max, Month == month[i],select= TG)$TG
  qu.min <- quantile(dat, 0.5)
  qu.max <- quantile(dat,(length(dat)-30)/length(dat))
  
  par(mfrow=c(1,1))
  png(file = paste("DataGenerated/DailyEVA/Mean_Residual_Life/",month.name[i],".png"), width = 1200, height = 500)
  mrlplot(dat, tlim=c(qu.min, qu.max))
  dev.off()
}

## --- Parameters stability plots

for(i in 1:12){
  dat <- subset(df_max, Month == month[i],select= TG)$TG
  qu.min <- quantile(dat, 0.5)
  qu.max <- quantile(dat,(length(dat)-30)/length(dat))
  
  png(file = paste("DataGenerated/DailyEVA/Parameters_stability/",month.name[i],".png"), width = 1200, height = 500)
  par(mfrow=c(1,2))
  tcplot(dat,tlim=c(qu.min, qu.max))
  dev.off()
}
data <- subset(df_max, Month == month[8],select= c(date,TG))
colnames(data) <- c("time","obs")
data <- clust(data,quantile(data$obs,0.7))
diplot(data,u.range = c(24,37))

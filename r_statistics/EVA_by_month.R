setwd("~/Documents/SCV/SCV_project3/notebooks")

library(evd)
library(ismev)
library(stats)
library(nlme)
library(POT)
library(eva)


period = 365.25

#--- Max temperature data processing
df_max <- read.delim("../data/observatoire-geneve/TX_STAID000241.txt", header = FALSE, sep=",", skip=20)
colnames(df_max) <- c("SOUID", "date", "TG", "Q_TG")
df_max <- df_max[df_max$Q_TG != '9' ,]
df_max$TG<-df_max$TG/10
df_max$Datenum <- df_max$date
df_max$index <-  seq(from = 1, to = length(df_max$TG),by = 1)
df_max<- subset(df_max, select=-c(SOUID,Q_TG))
df_max$date <- as.Date(as.character(df_max$date), "%Y%m%d")

df_max$Year <- format(as.Date(df_max$date, format="%Y/%m/%d"),"%Y")
df_max$Month <- format(as.Date(df_max$date, format="%Y/%m/%d"),"%m")
df_max$Day <- format(as.Date(df_max$date, format="%Y/%m/%d"),"%d")

month <- unique(df_max$Month)

## ---- POT approach --- ##

for(i in 1:12){
  dat <- subset(df_max, Month == month[i],select= TG)$TG
  qu.min <- quantile(dat, 0.7)
  qu.max <- quantile(dat,(length(dat)-30)/length(dat))
  
  par(mfrow=c(1,1))
  png(file = paste("DataGenerated/DailyEVA/Mean_Residual_Life/",month.name[i],".png"), width = 1200, height = 500)
  mrlplot(dat, u.range=c(qu.min, qu.max))
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

## --- Rules of Thumb

th_thumb <- data.frame(row.names = c("90% quantile","rule of thumb 2","rule of thumb 3"))

for(i in 1:12){
  dat <- subset(df_max, Month == month[i],select= TG)$TG
  k1 <- sort(dat, decreasing = TRUE)[floor(sqrt(length(dat)))]
  k2 <- sort(dat, decreasing = TRUE)[floor(length(dat)^(2/3)/log(log(length(dat))))]
  th_thumb[,month.name[[i]]] <- c((quantile(dat,0.9)),k1,k2)
}

write.csv(th_thumb,"DataGenerated/DailyEVA/th_thumb.csv")

## --- Test for threshold selection

th_score <- data.frame(row.names = seq(1,31,1))
th_cvm <- data.frame(row.names = seq(1,31,1))
th_th <- data.frame(row.names = seq(1,31,1))
for(i in 1:12){
  dat <- subset(df_max, Month == month[i],select= TG)$TG
  qu.min <- quantile(dat, 0.80)
  qu.max <- quantile(dat,(length(dat)-30)/length(dat))
  
  score <- gpdSeqTests(dat, thresholds = seq(qu.min,qu.max,(qu.max-qu.min)/30), method = "pbscore",nsim= 50)
  cvm <- gpdSeqTests(dat, thresholds = seq(qu.min,qu.max,(qu.max-qu.min)/30), method = "cvm")
  
  th_score[month.name[[i]]] <- score$p.values
  th_cvm[month.name[[i]]] <- cvm$p.values
  th_th[month.name[[i]]] <- cvm$threshold
}

write.csv(th_score, file = "DataGenerated/DailyEVA/th_score.csv")
write.csv(th_cvm, file = "DataGenerated/DailyEVA/th_cvm.csv")
write.csv(th_th, file = "DataGenerated/DailyEVA/th_th.csv")

## --- Fit of the POT and diagnostics plots 
th_estimate <- read.csv("DataGenerated/DailyEVA/Parameters_stability/visual_estimate.csv")[-1]

POT_fit <-list()

for(i in 1:12){
  data <- subset(df_max, Month == month[i],select= c(index,TG))
  colnames(data) <- c("time","obs")
  dat <- clust(data = data,u = quantile(data$obs,0.90),tim.cond = 1,clust.max = TRUE)
  POT_fit$month.name[[i]] <- fpot(dat[,"obs"],threshold = quantile(dat[,"obs"],0.9),npp = 30.5)
  png(file = paste("DataGenerated/DailyEVA/Diag_plot/",month.name[i],".png"), width = 1200, height = 800)
  par(mfrow=c(2,2))
  plot(POT_fit$month.name[[i]])
  dev.off()
}

## --- Compute the confidence interval for the parameters
d <- rep(0.,12)
conf_int <- data.frame(sigma = d, shape = d,sigma.std = d,shape.std = d,sigma.low = d,
                       sigma.high = d, shape.low = d,shape.high = d,row.names = month.name)
deviance1 <- data.frame(dev = d,row.names = month.name)
for(i in 1:12){
  conf_int[month.name[i],] <- c(POT_fit$month.name[[i]]$estimate[[1]],POT_fit$month.name[[i]]$estimate[[2]],
                               POT_fit$month.name[[i]]$std.err[[1]],POT_fit$month.name[[i]]$std.err[[2]],
                               POT_fit$month.name[[i]]$estimate[[1]]-1.96*POT_fit$month.name[[i]]$std.err[[1]],
                               POT_fit$month.name[[i]]$estimate[[1]]+1.96*POT_fit$month.name[[i]]$std.err[[1]],
                               POT_fit$month.name[[i]]$estimate[[2]]-1.96*POT_fit$month.name[[i]]$std.err[[2]],
                               POT_fit$month.name[[i]]$estimate[[2]]+1.96*POT_fit$month.name[[i]]$std.err[[2]])
  deviance1[month.name[i],] <- c(POT_fit$month.name[[i]]$deviance)
}

write.csv(conf_int, file = "DataGenerated/DailyEVA/POT_estimation.csv")
write.csv(deviance1, file = "DataGenerated/DailyEVA/POT_deviance.csv")

## --- Plot of the profile Likelihood

for(i in 1:12){
  if(i != 2 & i!=4){
    png(file = paste("DataGenerated/DailyEVA/Prof_Likelihood/",month.name[i],".png"), width = 1200, height = 400)
    par(mfrow=c(1,2))
    plot(profile(POT_fit$month.name[[i]]))
    abline(v=0,col=2,lty=2)
    dev.off()
  }
}

## --- Fit of the Gumbel for some month

dd <- c(1,3,5,6,7,8,9,10,11,12)
Gumbel_fit <-list()

for(i in dd){
  data <- subset(df_max, Month == month[i],select= c(index,TG))
  colnames(data) <- c("time","obs")
  dat <- clust(data = data,u = quantile(data$obs,0.90),tim.cond = 1,clust.max = TRUE)
  Gumbel_fit$month.name[[i]] <- fpot(dat[,"obs"],threshold = quantile(dat[,"obs"],0.9),npp = 30.5,shape = 0)
  png(file = paste("DataGenerated/DailyEVA/Diag_plot_gumbel/",month.name[i],".png"), width = 1200, height = 800)
  par(mfrow=c(2,2))
  plot(Gumbel_fit$month.name[[i]])
  dev.off()
}

## --- Compute the confidence interval for the parameters of the Gumbel fit

d <- rep(0.,10)
conf_int_gumbel <- data.frame(sigma = d,sigma.std = d,sigma.low = d,
                       sigma.high = d,row.names = month.name[dd])
deviance2 <- data.frame(dev = d,row.names = month.name)
for(i in dd){
  conf_int_gumbel[month.name[i],] <- c(Gumbel_fit$month.name[[i]]$estimate[[1]],
                                       Gumbel_fit$month.name[[i]]$std.err[[1]],
                                       Gumbel_fit$month.name[[i]]$estimate[[1]]-1.96*Gumbel_fit$month.name[[i]]$std.err[[1]],
                                       Gumbel_fit$month.name[[i]]$estimate[[1]]+1.96*Gumbel_fit$month.name[[i]]$std.err[[1]])
  deviance2[month.name[i],] <- c(Gumbel_fit$month.name[[i]]$deviance)
}

write.csv(conf_int_gumbel, file = "DataGenerated/DailyEVA/Gumbel_estimation.csv")
write.csv(deviance2, file = "DataGenerated/DailyEVA/Gumbel_deviance.csv")

## --- Likelihood ratio test between  the POT and the Gumbel model

p_val <- data.frame(dev = d, p_value = d, row.names = month.name[dd])
for(i in dd){
  p_val[month.name[i],] <- c(Gumbel_fit$month.name[[i]]$deviance-POT_fit$month.name[[i]]$deviance,
                              1-pchisq(Gumbel_fit$month.name[[i]]$deviance-POT_fit$month.name[[i]]$deviance,1))
}

write.csv(p_val, file = "DataGenerated/DailyEVA/Likelihood_ratio_p_val.csv")


## --- Return level 

return_POT <- function(j, period){
  data <- subset(df_max, Month == month.name[[j]],select= c(index,TG))
  return_level <- POT_fit$month.name[[j]]$threshold + POT_fit$month.name[[j]]$est[[1]]/POT_fit$month.name[[j]]$est[[2]]*((period*30.5*POT_fit$month.name[[j]]$pat)^(POT_fit$month.name[[j]]$est[[2]])-1)
}

return_Gumbel <- function(j, period){
  return_l <- Gumbel_fit$month.name[[j]]$threshold + Gumbel_fit$month.name[[j]]$est[[1]]*log(period* Gumbel_fit$month.name[[j]]$pat)
}

d <- rep(0,12)
return_levels <- data.frame(r10 = d, r20 = d, r50 = d, r100 = d,r200 = d, r1000 = d,max_obs = d, row.names = month.name)

period <- c(10,20,50,100,200,1000)

for(i in 1:6){
  return_levels[month.name[[2]],i] <- return_POT(1, period[i])
}
return_levels[month.name[[2]],7] <- max(subset(df_max, Month == month[2],select= TG))

for(i in 1:6){
  return_levels[month.name[[4]],i] <- return_POT(1, period[i])
}
return_levels[month.name[[4]],7] <- max(subset(df_max, Month == month[2],select= TG))

c <- c(1,3,5,6,7,8,9,10,11,12)

for(cc in c){
  for(i in 1:6){
    return_levels[month.name[[cc]],i] <- return_Gumbel(cc, period[i])
  }
  return_levels[month.name[[cc]],7] <- max(subset(df_max, Month == month[cc],select= TG))
  
}


write.csv(return_levels, file = "DataGenerated/DailyEVA/return_levels.csv")


## -- Profile Likelihood of the return levels
return_levels
data <- subset(df_max, Month == month[2],select= c(index,TG))
colnames(data) <- c("time","obs")
dat <- clust(data = data,u = quantile(data$obs,0.90),tim.cond = 1,clust.max = TRUE)
fit2<-gpd.fit(dat,threshold=quantile(data$obs,0.90), npy=30.5)
gpd.prof(z=fit2, m=5, xlow=13, xup=20, npy = 30.5, conf = 0.95)




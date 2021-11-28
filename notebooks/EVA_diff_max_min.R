setwd("~/Documents/SCV/SCV_project3/notebooks")

library(evd)
library(ismev)

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


#--- Min temperature data processing
df_min <- read.delim("../data/observatoire-geneve/TN_STAID000241.txt", header = FALSE, sep=",", skip=20)
colnames(df_min) <- c("SOUID", "date", "TG", "Q_TG")
df_min <- df_min[df_min$Q_TG != '9' ,]
df_min$TG<-df_min$TG/10
df_min<- subset(df_min, select=-c(SOUID,Q_TG))
df_min$date <- as.Date(as.character(df_min$date), "%Y%m%d")

df_min$Year <- format(as.Date(df_min$date, format="%Y/%m/%d"),"%Y")
df_min$Month <- format(as.Date(df_min$date, format="%Y/%m/%d"),"%m")
df_min$Day <- format(as.Date(df_min$date, format="%Y/%m/%d"),"%d")

#unique(df_min$date ==df_max$date) #check of corresponding date

# Merge of the data
df <- data.frame(date = df_max$date,max = df_max$TG, min = df_min$TG,
                 diff = df_max$TG - df_min$TG, Year = df_max$Year,
                Month = df_max$Month, Day = df_max$Day, index = df_max$index)
month <- unique(df$Month)
mean_month <- c()

for(i in 1:12){mean_month <- c(mean_month,mean(as.matrix(subset(df,Month==month[i],select = c(diff)))))}
df$diff_rescale <- df$diff
for(i in 1:length(df$diff)){df$diff_rescale[i] <- df$diff_rescale[i]-mean_month[which(month == df$Month[i])]}


par(mfrow=c(1,1))
plot(df$date,df$diff_rescale)


###### --- Peaks Over Threshold approach (POT) --- ######

qu.min <- quantile(df$diff_rescale, 0.5)
qu.max <- quantile(df$diff_rescale,(length(df$diff_rescale)-30)/length(df$diff_rescale))
mrlplot(df$diff_rescale, tlim=c(qu.min, qu.max))

par(mfrow=c(1,2))
tcplot(df$diff_rescale,tlim=c(qu.min, qu.max))


th <- 9
## Number of observation per year: 261 or 262
# table(substr(dowjones[,1],1,stop=4))
fit<-fpot(df$diff_rescale,threshold=th,npp=period)
par(mfrow=c(2,2))
plot(fit)

fit2<-gpd.fit(df$diff_rescale,threshold=th, npy=period)
gpd.diag(fit2)

par(mfrow=c(1,2))
plot(profile(fit))
abline(v=0,col=2,lty=2)

fit.gum<-fpot(df$diff_rescale, threshold=th, npp=period, shape=0)
par(mfrow=c(2,2))
plot(fit.gum)

rl10 <- th + fit$est[1]/fit$est[2]*((3652.5*fit$pat)^(fit$est[2])-1)
rl100 <- th + fit$est[1]/fit$est[2]*((36525*fit$pat)^(fit$est[2])-1)
as.matrix(scale(df$date))
fit<-gpd.fit(df$diff_rescale,threshold=th,ydat=as.matrix(scale(df$date)),sigl=1,siglink=exp)
gpd.diag(fit)

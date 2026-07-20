rm(list=ls())
library(stringr)

d <- read.delim('waarnemingen_species_records.tsv')

idx <- duplicated(d$species) #some species have multiple subspecies with records
sum(idx) #77 duplicates

species.duplicates <- d$species[idx]
idx2 <- which(d$species %in% species.duplicates)
d.duplicates <- d[idx2,] #examine the species with multiple subspecies recorded

#remove records tagged with Family or Genus level
idx3 <- which(str_trim(d$taxonRank) %in% c('CLASS', 'FAMILY', 'GENUS'))
d <- d[-idx3,]

#merge records by species over all subspecies and synonymous species
dt <- aggregate( numberOfOccurrences ~ species, data=d, sum)
anyDuplicated(dt$species) #check

#remove duplicates from original data frame d
idx <- which(duplicated(d$species))
d2 <- d[-idx,]

#do a left join on dt with the original data frame d
dt2 <- merge(dt, d2, by='species')
anyDuplicated(dt2$species)

#remove hybrids
hybrids <- grep(' x ', dt2$species, value=TRUE) #11 hybrids
hybrids.idx <- grep(' x ', dt2$species)
dt3 <- dt2[-hybrids.idx,]

#remove unnecessary columns from data.frame
anyDuplicated(str_trim(dt3$species)) #good
anyDuplicated(dt3$speciesKey) #good- all uniquely identified species
dt4 <- dt3[,c('species','speciesKey','numberOfOccurrences.x','family','iucnRedListCategory')]
colnames(dt4)[3] <- 'occurences'
dt4$species <- str_trim(dt4$species) #trim whitespace
dt4$family <- str_trim(dt4$family)
hist(dt4$occurences)

#save data.frame as RDS for easy access later
saveRDS(dt4, file='waarnemingen_occurrences_clean.RDS')













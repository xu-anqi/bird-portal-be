SELECT datasetKey, datasetname, publisher, COUNT(*)
FROM occurrence 
WHERE countryCode = 'BE' AND class = 'Aves'
GROUP BY datasetKey, datasetname, publisher

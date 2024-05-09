-- SQL script that ranks country origins of bands, ordered by the number of fans
SELECT origin, SUM(nb_fans) AS nb_fans
FROM metal_bands
GROUP BY origin
ORDER BY nb-fans DESC;
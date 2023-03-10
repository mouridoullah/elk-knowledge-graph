SELECT ?populaltion ?paysLabel ?abstract
WHERE {
  wd:Q90 wdt:P1082 ?populaltion;
                        wdt:P17 ?pays.
  OPTIONAL {
    wd:Q90 schema:description ?abstract.
    FILTER (lang(?abstract) = "fr")
  }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}



SELECT DISTINCT ?city ?cityLabel ?paysLabel ?abstract ?population ?coordinates
WHERE {
  ?city wdt:P31 wd:Q515;
        wdt:P1082 ?population;
        wdt:P17 ?pays.
  OPTIONAL {
    ?city schema:description ?abstract.
    FILTER (lang(?abstract) = "fr")
  }
  OPTIONAL {
    ?city wdt:P625 ?coordinates.
  }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
LIMIT 5


-- Oui, la clause "?city wdt:P625 ?coordinates" correspond à la récupération des coordonnées géographiques de la ville en question. 
-- Les coordonnées sont généralement exprimées en latitude et longitude, sous la forme d'un point géographique.
-- Par exemple, si la requête renvoie les coordonnées suivantes pour une ville : "Point(-0.1277583 51.5073509)", cela signifie que la ville est située à une longitude de -0.1277583 degrés et à une latitude de 51.5073509 degrés. 
-- Les coordonnées sont exprimées en utilisant le format "Point(longitude latitude)", conformément à la convention de représentation géographique de WGS84.



-- SELECT ?populaltion ?paysLabel ?abstract ?coordinates ?airport ?port ?nearbyCityLabel 
-- WHERE {
--   wd:Q90 wdt:P1082 ?populaltion; wdt:P17 ?pays.
--   OPTIONAL {
--     wd:Q90 schema:description ?abstract.
--     FILTER (lang(?abstract) = "fr")
--   }
--   OPTIONAL {
--     wd:Q90 wdt:P625 ?coordinates.
--   }
  
--   OPTIONAL {
--     ?nearbyCity wdt:P131* wd:Q90.
--     ?nearbyCity rdfs:label ?nearbyCityLabel.
--     FILTER (lang(?nearbyCityLabel) = "fr")
--     FILTER (?nearbyCity != wd:Q90)
--   }
--   OPTIONAL {
--     ?airport wdt:P17 ?pays ;
--              wdt:P31/wdt:P279* wd:Q1248784 ;
--              wdt:P131 wd:Q90.
--   }
--   OPTIONAL {
--     ?port wdt:P17 ?pays ;
--           wdt:P31/wdt:P279* wd:Q39546 ;
--           wdt:P131 wd:Q90.
--   }
--   SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
-- }



-- SELECT ?population ?paysLabel ?abstract ?coordinates ?airport ?port (GROUP_CONCAT(DISTINCT ?nearbyCityLabel; separator=", ") AS ?nearbyCities)
-- WHERE {
--   wd:Q90 wdt:P1082 ?population; wdt:P17 ?pays.
--   OPTIONAL {
--     wd:Q90 schema:description ?abstract.
--     FILTER (lang(?abstract) = "fr")
--   }
--   OPTIONAL {
--     wd:Q90 wdt:P625 ?coordinates.
--   }
  
--   OPTIONAL {
--     ?nearbyCity wdt:P131* wd:Q90.
--     ?nearbyCity rdfs:label ?nearbyCityLabel.
--     FILTER (lang(?nearbyCityLabel) = "fr")
--     FILTER (?nearbyCity != wd:Q90)
--   }
--   OPTIONAL {
--     ?airport wdt:P17 ?pays ;
--              wdt:P31/wdt:P279* wd:Q1248784 ;
--              wdt:P131 wd:Q90.
--   }
--   OPTIONAL {
--     ?port wdt:P17 ?pays ;
--           wdt:P31/wdt:P279* wd:Q39546 ;
--           wdt:P131 wd:Q90.
--   }

--   OPTIONAL {
--     ?city wdt:P131 wd:Q90;
--           wdt:P17 ?country.
--     SERVICE <weather-api> {
--         ?weatherData <weather-property> ?weatherValue.
--         FILTER(?cityLabel = <city-name> && ?countryLabel = <country-name>)
--     }
--  }
--   SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
-- }
-- GROUP BY ?population ?paysLabel ?abstract ?coordinates ?airport ?port



SELECT ?population ?paysLabel ?abstract ?coordinates ?autoroute ?airport ?port ?density ?ageDistribution ?birthRate ?deathRate (GROUP_CONCAT(DISTINCT ?nearbyCityLabel; separator=", ") AS ?nearbyCities)
WHERE {
  wd:Q90 wdt:P1082 ?population; wdt:P17 ?pays.
  OPTIONAL {
    wd:Q90 schema:description ?abstract.
    FILTER (lang(?abstract) = "fr")
  }
  OPTIONAL {
    wd:Q90 wdt:P625 ?coordinates.
  }
  
  OPTIONAL {
    ?nearbyCity wdt:P131* wd:Q90.
    ?nearbyCity rdfs:label ?nearbyCityLabel.
    FILTER (lang(?nearbyCityLabel) = "fr")
    FILTER (?nearbyCity != wd:Q90)
  }
  OPTIONAL {
    ?airport wdt:P17 ?pays ;
             wdt:P31/wdt:P279* wd:Q1248784 ;
             wdt:P131 wd:Q90.
  }
  OPTIONAL {
    ?port wdt:P17 ?pays ;
          wdt:P31/wdt:P279* wd:Q39546 ;
          wdt:P131 wd:Q90.
  }
  OPTIONAL {
  ?autoroute wdt:P17 ?pays ;
             wdt:P31/wdt:P279* wd:Q34442 ;
             wdt:P131 wd:Q90.
  }
  
  OPTIONAL { wd:Q90 wdt:P108 ?density. }
  OPTIONAL { wd:Q90 wdt:P2044 ?ageDistribution. }
  OPTIONAL { wd:Q90 wdt:P1582 ?birthRate. }
  OPTIONAL { wd:Q90 wdt:P2566 ?deathRate. }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
GROUP BY ?population ?paysLabel ?abstract ?coordinates ?airport ?port ?density ?ageDistribution ?birthRate ?deathRate ?autoroute




-- # Airports within 100km from Berlin
-- #defaultView:Map
-- SELECT ?place ?placeLabel ?location ?dist 
-- WHERE {
--   # Berlin coordinates
--   wd:Q64 wdt:P625 ?berlinLoc . 
--   SERVICE wikibase:around { 
--       ?place wdt:P625 ?location . 
--       bd:serviceParam wikibase:center ?berlinLoc . 
--       bd:serviceParam wikibase:radius "100" . 
--       bd:serviceParam wikibase:distance ?dist.
--   } 
--   FILTER EXISTS {
--     # Is an airport
--     ?place wdt:P31/wdt:P279* wd:Q1248784 .
--   }
--   SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } 
-- } 
-- ORDER BY ASC(?dist)
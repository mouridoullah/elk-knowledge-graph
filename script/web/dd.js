var query = encodeURIComponent(
    "SELECT distinct ?titre ?resume ?date ?wiki ?photo "+
    "WHERE { "+
      "?film a <http://dbpedia.org/ontology/Film> ; "+
          "dbpedia-owl:abstract ?resume ;"+
          "rdfs:label ?titre ;"+
          "dbpprop:released ?date ;"+
          "foaf:isPrimaryTopicOf ?wiki ;"+
          "dbpedia-owl:thumbnail ?photo "+
  "FILTER langMatches(lang(?resume), 'fr')"+
  "FILTER langMatches(lang(?titre), 'fr')"+
  "}"+
  "LIMIT 10");
  
  var url = 'http://dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fdbpedia.org&query='+ query +'&output=json';
  //console.log(url);
  
  //$('div').append(url);
  
  $.getJSON(url+"&callback=?", function(resultats) {
    $(resultats.results.bindings).each(function(i) {
      $('div').append("<strong>" + resultats.results.bindings[i].titre.value + "</strong>");
      
      $('div').append('<p>' + resultats.results.bindings[i].resume.value + '</p>');
      
      $('div').append('<span>Voici la page Wikipédia du film: </span>');
      
      $('div').append("<a href='" + resultats.results.bindings[i].wiki.value + "' title='"+ resultats.results.bindings[i].titre.value +"'>"+ resultats.results.bindings[i].wiki.value+ "</a>");
  
      $('div').append('<br />');
      $('div').append("<img src='" + resultats.results.bindings[i].photo.value.replace(/commons/,"en") + "' />");
      $('div').append('<br />');
    });
  });
  
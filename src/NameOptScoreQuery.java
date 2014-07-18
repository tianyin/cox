import java.io.IOException;
import java.util.HashSet;
import java.util.Set;
import java.util.HashMap;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.AtomicReader;
import org.apache.lucene.index.AtomicReaderContext;
//import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.Term;
import org.apache.lucene.queries.CustomScoreProvider;
import org.apache.lucene.queries.CustomScoreQuery;
import org.apache.lucene.queries.function.FunctionQuery;
import org.apache.lucene.search.Query;
/**
 *
 * @author athrunarthur
 */
public class NameOptScoreQuery extends CustomScoreQuery {
  
    private final Query query;
    private final HashMap<String, String> synoms = new HashMap<String, String>();
    private final HashMap<String, String> ontologies = new HashMap<String, String>();
 

    NameOptScoreQuery(Query query, FunctionQuery boostQuery) {
        super(query, boostQuery);
        this.query = query;
	synoms.put("option", "opt");
	synoms.put("permission", "perm");
	synoms.put("crash", "fail");
	ontologies.put("tcp", "network");
	ontologies.put("encrypt", "ssl");
    }
 
    public CustomScoreProvider getCustomScoreProvider(final AtomicReaderContext ctx) {
        return new CustomScoreProvider(ctx) {
            @Override
            public float customScore(int doc,
                    float subQueryScore,
                    float valSrcScore) throws IOException {
                AtomicReader reader = ctx.reader();
                Document d = reader.document(doc);
                String opt = d.get("op_name").toLowerCase().replace("mapreduce", "");
                Set<Term> ts = new HashSet<Term>();
                query.extractTerms(ts);
                double match_terms = 1;
                for(Term t : ts)
                {
                    if(opt.indexOf(t.text().toLowerCase()) != -1 )
                    {
                        match_terms ++;
                    }
		    else if (synoms.containsKey(t.text()))
		    {
			    if (opt.indexOf(synoms.get(t.text())) != -1)
			    {
			    match_terms ++;
			    }
		    }
		    if (ontologies.containsKey(t.text()) && opt.indexOf(ontologies.get(t.text())) != -1)
		    {
			match_terms += 1;
		    }
                }
                
                
                return (float) (Math.sqrt(match_terms) * subQueryScore * valSrcScore);
            }
        };
    }
}


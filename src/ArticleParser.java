import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringReader;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;

import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.RAMDirectory;
import org.apache.lucene.util.Version;

/**
 * This class is used to parse a general article and get the words related to a parameter;
 * Currently, the idea is simple. We read a paragraph and check whether it contains only one parameter, 
 * if so, we identify these words as related to the parameter
 * 
 * Basically, we build index for each paragraph and go through the parameter list
 */
public class ArticleParser {
	public String tmpIndexDir = "/tmp/cox_temp_index/";
	public IndexWriterConfig iwc;
	public IndexWriter writer;
	
	public Set<String> parameterSet = new HashSet<String>();
	
	public ArticleParser(Collection<String> pSet) {
		iwc = new IndexWriterConfig(Version.LUCENE_47, new StandardAnalyzer(Version.LUCENE_47));
		iwc.setOpenMode(IndexWriterConfig.OpenMode.CREATE);
		parameterSet.addAll(pSet);
	}
	
	/**
	 * Given an article, do a parsing
	 * @param articlePath: the file path of an article
	 * @param outputDir:   the directory that store the results
	 */
	public void parse(String articlePath, String outputDir) {
		if(outputDir == null) {
			System.err.println("[ERROR] outputDir cannot be null");
		} else {
			File opDir = new File(outputDir);
			if(opDir.exists() == false) {
				opDir.mkdir();
			}
		}
		outputDir += "/";
		
		Map<String, String> paraMap = new HashMap<String, String>();

		try {
			//1. Put everything into a map
			FileReader read = new FileReader(new File(articlePath));
			BufferedReader reader = new BufferedReader(read);
			String paragraph = null;
			int counter = 1;
			while ((paragraph = reader.readLine()) != null) {
//				System.out.println(paragraph);
				paraMap.put(Integer.toString(counter++), paragraph);
			}
			
			//2. Build in-memory indexing for each paragraph
			RAMDirectory ramDir = new RAMDirectory(); // RAMDirectory: hold the in-memory representation of the index.
			IndexWriter writer = new IndexWriter(ramDir, iwc);
			
			Set<String> keyset = paraMap.keySet();
			Iterator<String> iterator = keyset.iterator();
			while(iterator.hasNext()) {
				String paraIndx = iterator.next(); 
				String paraText = paraMap.get(paraIndx);
				
				writer.addDocument(createDocument(paraIndx, paraText));	
			}
			writer.close();
			
			//3. Go through the parameter list and record the matches of each paragraph
			Map<String, Set<String>> paraParaCount = new HashMap<String, Set<String>>();
			
			IndexSearcher searcher = new IndexSearcher(DirectoryReader.open(ramDir));
			
			Iterator<String> pIter = parameterSet.iterator();
			while(pIter.hasNext()) {
				String parameter = pIter.next();
				Set<String> pIndices = search(searcher, parameter, paraMap);
				
				Iterator<String> piIter = pIndices.iterator();
				while(piIter.hasNext()) {
					String pIndex = piIter.next();
					if(paraParaCount.containsKey(pIndex) == false) {
						paraParaCount.put(pIndex, new HashSet<String>());
					}
					Set<String> parameters = paraParaCount.get(pIndex);
					parameters.add(parameter);
				}
			}
			
			//4. Go over paraParaCount and delete all paragraphs with more than 1 parameters
			Set<String> pSet = paraParaCount.keySet();
			Iterator<String> pgIter = pSet.iterator();
			while(pgIter.hasNext()) {
				String pgIdx = pgIter.next();
				Set<String> pmSet = paraParaCount.get(pgIdx);
				
				//[Testing] Print the information
//				System.out.println("=====================================================");
//				System.out.println(pgIdx + " " + pmSet.size());
//				Iterator<String> pmIter = pmSet.iterator();
//				while(pmIter.hasNext()) {
//					String pm = pmIter.next();
//					System.out.print(pm + ", ");
//				}
//				System.out.println();
//				String content = paraMap.get(pgIdx);
//				System.out.println(content);
				
				if(pmSet.size() == 1) {
					//TODO: append to the parameter file in outputDir
					//get parameter
					String parameter = (String) (pmSet.toArray()[0]);
					File pFile = new File(outputDir + parameter);
					
					String content = paraMap.get(pgIdx);
					
					PrintWriter pWriter = new PrintWriter(new BufferedWriter(new FileWriter(pFile, true)));
					pWriter.println(content);
					pWriter.close();
				}
			}
			
		} catch (IOException e) {
			System.out.println("Exception in IndexFiles(): " + e.getMessage());
		} catch (ParseException e) {
			e.printStackTrace();
		}
	}
	
	private Set<String> search(IndexSearcher searcher, String queryString, Map<String, String> paragraphMap) 
			throws ParseException, IOException {
		
		Set<String> res = new HashSet<String>();
		
		QueryParser qparser = new QueryParser(Version.LUCENE_47, "content", new StandardAnalyzer(Version.LUCENE_47));
        Query query = qparser.parse(queryString);
        
        // Search for the query
        TopDocs results = searcher.search(query, paragraphMap.size());
        ScoreDoc[] hits = results.scoreDocs;
        
        for (ScoreDoc hit : hits) {
			// System.out.println(hits[i].doc);
			Document doc = searcher.doc(hit.doc);
			String paraKey = doc.get("index");
//			System.out.println(paraKey + "===> " + paragraphMap.get(paraKey));
			res.add(paraKey);
		}
        
        return res;
	}
	
    private static Document createDocument(String index, String content) {
        Document doc = new Document();

        // Add the title as an unindexed field...
        doc.add(new StringField("index", index, Field.Store.YES));

        // ...and the content as an indexed field. Note that indexed
        // Text fields are constructed using a Reader. Lucene can read
        // and index very large chunks of text, without storing the
        // entire content verbatim in the index. In this example we
        // can just wrap the content string in a StringReader.
        doc.add(new TextField("content", new StringReader(content)));

        return doc;
    }
    
    //FOR TESTING PURPOSE
	public static void main(String[] args) {
		//get the httpd parameter from the dataset
		Set<String> pSet = new HashSet<String>();
		File pDir = new File("/home/tixu/Cox/dataset/httpd/parameters/");
		String[] pArr = pDir.list();
		for(int i=0; i<pArr.length; i++) {
			pSet.add(pArr[i]);
		}
		
		ArticleParser aparse = new ArticleParser(pSet);
		aparse.parse("/home/tixu/Cox/dataset/httpd/norm_manual/norm_logs", "/home/tixu/Cox/dataset/httpd/articles");
	}
}

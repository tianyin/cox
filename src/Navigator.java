import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.HashSet;
import java.util.Iterator;
import java.util.logging.FileHandler;
import java.util.logging.Level;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.PosixParser;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;
import org.apache.lucene.queries.function.FunctionQuery;
import org.apache.lucene.queries.CustomScoreQuery;
import org.apache.lucene.queries.function.valuesource.DoubleFieldSource;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;

/**
 * This class is the navigation client, it takes users' queries and returns the recommended parameters
 */
public class Navigator {
	private static final String name = IndexManualPages.class.getName();
	private static final Logger log = Logger.getLogger(name);
	private final String indexReposity;

	public String field = "op_desc";
	public int repeat = 0;
	public boolean raw = false;
	public int numOfResults = 50; //50 is a lot

	private IndexSearcher searcher;
	private Analyzer analyzer;
	private QueryParser parser;
	private boolean optimization;

	//must to set options should not be returned to users, because users are definitely not looking for them
	private HashSet<String> mustSetOpts = null;
	
	/**
	 * Constructor
	 * @param indexRepo: the place the indices are stored
	 * @param improve: TODO
	 */
	public Navigator(String indexRepo, String filterFile, boolean ipv, boolean strict) {
		indexReposity = indexRepo;
		optimization  = ipv;

		try {
			IndexReader reader = DirectoryReader.open(FSDirectory.open(new File(indexReposity)));
			searcher = new IndexSearcher(reader);
			// analyzer = new StandardAnalyzer(Version.LUCENE_46);
			// analyzer = new EnglishAnalyzer(Version.LUCENE_46);
			analyzer = new CAnalyzer(Version.LUCENE_47).getAnalyzer();
			
			parser = new QueryParser(Version.LUCENE_47, field, analyzer);
			if(strict == true) {
				parser.setDefaultOperator(QueryParser.AND_OPERATOR);
			}
			
			getMustSetOpts(filterFile);
		
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	/**
	 * search the parameter based on the user's query
	 * @param queryString: the query (string) of the user
	 * @return: a list of parameters 
	 */
	public List<String> navigate(String queryString) {
		try {
			queryString = queryString.trim();
//			System.out.println("QUERY STRING: " + queryString);
			
			Query query = parser.parse(queryString);
			return navigate(query);
			
		} catch (ParseException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}

		return null;
	}

	/**
	 * This function do the real navigation jobs
	 * @param query: the query string
	 * @return: a list of parameters
	 * @throws IOException
	 */
	private List<String> navigate(Query query) throws IOException {
		FunctionQuery boostQuery = new FunctionQuery(new DoubleFieldSource("boost"));
		Query q;
		if (optimization) {
			q = new NameOptScoreQuery(query, boostQuery);
		} else {
			q = new CustomScoreQuery(query, boostQuery);
		}

		TopDocs results = searcher.search(q, numOfResults);
		ScoreDoc[] hits = results.scoreDocs;

		List<String> res = new ArrayList<String>();

		log.log(Level.INFO, "match cases {0}", hits.length);
		for (ScoreDoc hit : hits) {
			// System.out.println(hits[i].doc);
			Document doc = searcher.doc(hit.doc);
			String path = doc.get("op_name");
			res.add(path);
			// System.out.println("[" + hit.toString() + "]" + path);
		}
		
		if (optimization) {
			filterMustSetOpts(res);
		}
		
		return res;
	}
	
	protected void getMustSetOpts(String filterFile) {
		if (filterFile != null) {
			mustSetOpts = new HashSet<String>();
			
			try{
				BufferedReader bufferedReader = new BufferedReader(new FileReader(filterFile));
				String line = null;
				while( (line = bufferedReader.readLine()) != null) {
					line = line.trim();
					mustSetOpts.add(line);
				}
				bufferedReader.close();
			} catch(IOException e) {
				e.printStackTrace();
			}
		}
	}

	protected void filterMustSetOpts(List<String> opts) {
		if (mustSetOpts != null) {
			Iterator<String> iter = opts.iterator();
			while (iter.hasNext()) {
				String s = iter.next();
				if (mustSetOpts.contains(s)) {
					iter.remove();
				}
			}
		}
	}

	protected static CommandLine parse_args(String[] args) {		
		CommandLineParser parser = new PosixParser();
		Options opts = new Options();
		opts.addOption(new Option("a", false, "enable all coxy optimization"));
		opts.addOption(new Option("s", false, "use strict mode: all the keywords must be matched"));
		
		opts.addOption(new Option("q", true,  "query string to find the parameter"));
		opts.addOption(new Option("i", true,  "the path of the indexes"));
		opts.addOption(new Option("f", true,  "the path of the input file (containing the queries)"));
		opts.addOption(new Option("o", true,  "the path of the output file (results)"));
		opts.addOption(new Option("x", true,  "the path of the filter file (containing parameters not to expose to users"));
		
		try {
			CommandLine cmd = parser.parse(opts, args);
			
			if (cmd.hasOption("i") == false) {
				System.out.println("index path is required!");
				HelpFormatter formatter = new HelpFormatter();
				formatter.printHelp("ant", opts);
				System.exit(-1);
			}
			
			if (cmd.hasOption("o") == false) {
				System.out.println("you are required to set an output file. Sorry fot this.");
				HelpFormatter formatter = new HelpFormatter();
				formatter.printHelp("ant", opts);
				System.exit(-1);
			}
			
			if (cmd.hasOption("f") == false && cmd.hasOption("q") == false) {
				System.out.println("Either a query string is required or an input file is required!");
				HelpFormatter formatter = new HelpFormatter();
				formatter.printHelp("ant", opts);
				System.exit(-1);
				
			} else if(cmd.hasOption("f") == true && cmd.hasOption("q") == true) {
				System.out.println("Please only specify one input method!");
				HelpFormatter formatter = new HelpFormatter();
				formatter.printHelp("ant", opts);
				System.exit(-1);
			}
			
			return cmd;

		} catch (org.apache.commons.cli.ParseException e) {
			System.out.println("unexpected exception in parse_args(): " + e.getLocalizedMessage());
			return null;
		}
	}

	protected static void search_main(String[] args) throws Exception {
		CommandLine cmd = parse_args(args);
		
		Navigator searcher = new Navigator(cmd.getOptionValue("i"), cmd.getOptionValue("x"), cmd.hasOption("a"), cmd.hasOption("s"));
		
		//This list contains all the query strings
		List<String> queryStrList = new LinkedList<String>();
		
		//Put the inputed query strings into the list
		if(cmd.hasOption("q")) {
			queryStrList.add(cmd.getOptionValue("q").trim());
			
		} else if(cmd.hasOption("f")) {
			BufferedReader bufferedReader = new BufferedReader(new FileReader(cmd.getOptionValue("f")));
			String line = null;
			while( (line = bufferedReader.readLine()) != null) {
				line = line.trim();
				log.info("searching query " + line);
				queryStrList.add(line);
			}
			bufferedReader.close();
		}
		
		BufferedWriter writer = new BufferedWriter(new FileWriter(cmd.getOptionValue("o")));
		
		//do work
		Iterator<String> iterator = queryStrList.iterator();
		while(iterator.hasNext()) {
			String queryStr = iterator.next();
			log.info("searching query " + queryStr);
			List<String> opts = searcher.navigate(queryStr);
			
			writer.write(queryStr);
			writer.write(" | ");
			for (String s : opts) {
				writer.write(s + " | ");
			}
			writer.write("\n");
		}
		writer.flush();
		writer.close();
	}

	/**
	 * Command-line based navigation
	 * @param args: see the parse_args function
	 * @throws Exception
	 */
	public static void main(String[] args) throws Exception {
		log.setUseParentHandlers(false);
		try {
			FileHandler fh = new FileHandler("search.log");
			log.addHandler(fh);
			SimpleFormatter formatter = new SimpleFormatter();
			fh.setFormatter(formatter);
		} catch (Exception e) {
			System.out.println("Unexpected exception : " + e.getMessage());
		}
		search_main(args);
	}
}

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.HashSet;
import java.util.Iterator;
import java.util.logging.FileHandler;
import java.util.logging.Level;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.OptionBuilder;
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

public class Navigator {
	
	private static final String name = IndexFiles.class.getName();
	private static final Logger log = Logger.getLogger(name);
	private final String indexReposity;

	public String field = "op_desc";
	public int repeat = 0;
	public boolean raw = false;
	public int hitsPerPage = 10;

	private IndexSearcher searcher;
	private Analyzer analyzer;
	private QueryParser parser;
	private boolean improve;

	/**
	 * Constructor
	 * @param indexRepo: the place the indices are stored
	 * @param improve: TODO
	 */
	public Navigator(String indexRepo, boolean ipv) {
		indexReposity = indexRepo;
		improve       = ipv;

		try {
			IndexReader reader = DirectoryReader.open(FSDirectory.open(new File(indexReposity)));
			searcher = new IndexSearcher(reader);
			// analyzer = new StandardAnalyzer(Version.LUCENE_46);
			// analyzer = new EnglishAnalyzer(Version.LUCENE_46);
			analyzer = new CAnalyzer(Version.LUCENE_47).getAnalyzer();
			parser = new QueryParser(Version.LUCENE_47, field, analyzer);
			// reader.close();
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
		if (improve) {
			q = new NameOptScoreQuery(query, boostQuery);
		} else {
			q = new CustomScoreQuery(query, boostQuery);
		}

		// Collect enough docs to show 5 pages
		TopDocs results = searcher.search(q, 5 * hitsPerPage);
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
		
		if (improve) {
			res = filter_must_set_opts(res);
		}
		
		return res;
	}

	protected static List<String> order_by_name(String query, List<String> res) {
		return res;
	}

	protected static List<String> filter_must_set_opts(List<String> opts) {
		HashSet<String> must_set_opts = new HashSet<String>();
		must_set_opts.add("ServerRoot");
		must_set_opts.add("Listen");
		must_set_opts.add("DocumentRoot");
		Iterator<String> iter = opts.iterator();
		while (iter.hasNext()) {
			String s = iter.next();
			if (must_set_opts.contains(s)) {
				System.out.println(s + " is removed due to must_set_opts!\n");
				iter.remove();
			}
		}

		return opts;
	}

	protected static HashMap<String, String> parse_args(String[] args) {
		HashMap<String, String> res = new HashMap<String, String>();
		CommandLineParser parser = new PosixParser();
		Options opts = new Options();
		opts.addOption(new Option("a", "improve via icon"));
		
		opts.addOption(OptionBuilder.withArgName("index-path").hasArg().withDescription("indexing file's path").create("i"));
		opts.addOption(OptionBuilder.withArgName("input-file").hasArg().withDescription("popularity file path").create("f"));
		opts.addOption(OptionBuilder.withArgName("output-file").hasArg().withDescription("output file path").create("o"));
		
		try {
			CommandLine cmd = parser.parse(opts, args);
			if (cmd.hasOption("i")) {
				res.put("index-path", cmd.getOptionValue("i"));
			} else {
				System.out.println("index-path is required!");
				HelpFormatter formatter = new HelpFormatter();
				formatter.printHelp("ant", opts);
				System.exit(-1);
			}
			if (cmd.hasOption("f")) {
				res.put("input-file", cmd.getOptionValue("f"));
			} else {
				System.out.println("input-file is required!");
				HelpFormatter formatter = new HelpFormatter();
				formatter.printHelp("ant", opts);
				System.exit(-1);
			}
			if (cmd.hasOption("o")) {
				res.put("output-file", cmd.getOptionValue("o"));
			} else {
				System.out.println("output-file is required!");
				HelpFormatter formatter = new HelpFormatter();
				formatter.printHelp("ant", opts);
				System.exit(-1);
			}
			if (cmd.hasOption("a")) {
				res.put("improve-icon", "true");
			} else {
				res.put("improve-icon", "false");
			}

		} catch (org.apache.commons.cli.ParseException e) {
			System.out.println("unexpected exception in parse_args(): " + e.getLocalizedMessage());
		}

		return res;
	}

	protected static void search_main(String[] args) throws Exception {

		HashMap<String, String> params = parse_args(args);
		// System.out.println("start searching with ");
		// System.out.println("\t improve-icon : " +
		// params.get("improve-icon"));
		Navigator searcher = new Navigator(params.get("index-path"), params.get("improve-icon") == "true");
		FileReader read = new FileReader(new File(params.get("input-file")));
		BufferedReader reader = new BufferedReader(read);
		String content = reader.readLine();
//		String d = "|";
		FileWriter write = new FileWriter(new File(params.get("output-file")));
		BufferedWriter writer = new BufferedWriter(write);

		while (content != null) {
			content = content.trim();
			log.info("searching query " + content);
			List<String> opts = searcher.navigate(content);
			writer.write(content);
			writer.write(" | ");
			for (String s : opts) {
				writer.write(s + " | ");
			}
			writer.write("\n");
			content = reader.readLine();
		}
		reader.close();
		writer.close();
		write.close();
		read.close();
	}

	/** Simple command-line based search demo. */
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
		// SearchFiles searcher = new
		// SearchFiles("/Users/athrunarthur/xuepeng/icon/index/httpd/");

		// List<String> opts = searcher.search("name");
		// System.out.println("return opts " + opts.size());
	}
}

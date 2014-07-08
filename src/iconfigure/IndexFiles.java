package iconfigure;

/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.LongField;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;

import org.apache.lucene.index.Term;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;

import core.CAnalyzer;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.StringReader;
import java.util.Date;
import java.util.HashMap;
import java.util.logging.FileHandler;
import java.util.logging.Level;

import org.apache.lucene.index.*;

import org.apache.commons.cli.*;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;
import org.apache.lucene.document.DoubleDocValuesField;



/**
 * Index all text files under a directory.
 */
public class IndexFiles {
    private static final String name = IndexFiles.class.getName();
    private static final Logger log = Logger.getLogger(name);
    
    protected static double boost_equation(double popularity)
    {
	    return Math.sqrt(popularity/* * 1000*/ + 0.1);
    }

    private static final double default_doc_boost = boost_equation(0);
    private final HashMap<String, Double> m_oConfigPopularities;
	private IndexFiles(String popularity_file) {
        this.m_oConfigPopularities = new HashMap<>();
            if (popularity_file != null)
            {
		    m_oConfigPopularities.put("RewriteRule", 1.0);
                try{
                    FileReader read = new FileReader(new File(popularity_file));
                    BufferedReader reader = new BufferedReader(read);
                    String content = reader.readLine();
                    while(content != null)
                    {
                        String[] lns = content.trim().split(":");
                        if(lns.length != 2)
                            continue;
                        String name = lns[0];
                        Double v = Double.parseDouble(lns[1]);
			v = boost_equation(v);
			//v = Math.log(v + 0.1);
                        m_oConfigPopularities.put(name, v);
                        //System.out.println("name " + name + " " + v);
                        content = reader.readLine();
                    }
                }
                catch(IOException e)
                {
                    System.out.println("Exception in IndexFiles(): " + e.getMessage());
                }
                
            }
        }

	public void indexDir(String indexRepo, String docRepo,
			boolean createOrAppend) {
		File docDir = new File(docRepo);
		if (!docDir.exists() || !docDir.canRead()) {
                        log.log(Level.SEVERE, "Document directory ''{0}'' does not exist or is not readable, please check the path", docDir.getAbsolutePath());
			System.exit(1);
		}

		Date start = new Date();
		try {
                    log.info("Indexing to directory " + indexRepo);

			Directory dir = FSDirectory.open(new File(indexRepo));
//			Analyzer analyzer = new EnglishAnalyzer(Version.LUCENE_46);
			CAnalyzer analyzer = new CAnalyzer(Version.LUCENE_46);
			IndexWriterConfig iwc = new IndexWriterConfig(Version.LUCENE_46, analyzer.getAnalyzer());

			if (createOrAppend) {
				// Create a new index in the directory, removing any previously
				// indexed documents:
				iwc.setOpenMode(IndexWriterConfig.OpenMode.CREATE);
			} else {
				// Add new documents to an existing index:
				iwc.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND);
			}

			// Optional: for better indexing performance, if you are indexing many documents, increase the RAM buffer 
			// But if you do this, increase the max heap size to the JVM (eg add -Xmx512m or -Xmx1g):
			// iwc.setRAMBufferSizeMB(256.0);

			IndexWriter writer = new IndexWriter(dir, iwc);
			indexDocs(writer, docDir);

			// NOTE: if you want to maximize search performance, you can optionally call forceMerge here. 
			// This can be a terribly costly operation, so generally it's only worth it when
			// your index is relatively static (i.e., you're done adding documents to it):
			// writer.forceMerge(1);

			writer.close();

			Date end = new Date();
                        log.log(Level.SEVERE, "Indexing time: ''{0}'' milliseconds ", end.getTime() - start.getTime());

		} catch (IOException e) {
                        log.log(Level.SEVERE, "caught a " + e.getClass() + " with message : "+ e.getMessage());
			System.out.println("Exception : check log!");
                        System.exit(-1);
		}
	}
	
	/**
	 * Indexes the given file using the given writer, or if a directory is
	 * given, recurses over files and directories found under the given directory.
	 * 
	 * NOTE: This method indexes one document per input file. This is slow.	 
	 * For good throughput, put multiple documents into your input file(s).
	 * An example of this is in the benchmark module, which can create "line doc" files, 
	 * one document per line, using the <a href=
	 * "../../../../../contrib-benchmark/org/apache/lucene/benchmark/byTask/tasks/WriteLineDocTask.html"
	 * >WriteLineDocTask</a>.
	 * 
	 * @param writer: Writer to the index where the given file/dir info will be stored
	 * @param file: The file to index, or the directory to recurse into to find files to index
	 * @throws IOException: If there is a low-level I/O error
	 */
	private void indexDocs(IndexWriter writer, File file) throws IOException {
		// do not try to index files that cannot be read
		if (file.canRead()) {
			if (file.isDirectory()) {
				String[] files = file.list();
				// an IO error could occur
				if (files != null) {
					for (int i = 0; i < files.length; i++) {
						indexDocs(writer, new File(file, files[i]));
					}
				}
			} else { // it is a file
				FileInputStream fis;
				try {
					fis = new FileInputStream(file);
				} catch (FileNotFoundException fnfe) {
					// at least on windows, some temporary files raise this
					// exception with an "access denied" message
					// checking if the file can be read doesn't help
					return;
				}

				try {
					// make a new, empty document
					Document doc = new Document();
                                        

					// Add the path of the file as a field named "path". Use a 
					// Use a field that is indexed (i.e. searchable), 
					// but don't tokenize the field into separate words and don't index term frequency
					// or positional information:
					String op_name = file.getName().replaceAll("<", "").replaceAll(">", "");
					doc.add(new StringField("path", file.getPath(), Field.Store.YES));
					doc.add(new StringField("op_name", op_name, Field.Store.YES));

					// Add the last modified date of the file a field named "modified".
					// Use a LongField that is indexed (i.e. efficiently filterable with
					// NumericRangeFilter). This indexes to millisecond resolution, which
					// is often too fine. You could instead create a number based on year/month/day/hour/minutes/seconds, 
					// down the resolution you require.
					// For example the long value 2011021714 would mean February 17, 2011, 2-3 PM.
					doc.add(new LongField("modified", file.lastModified(), Field.Store.NO));
					
					// Add the contents of the file to a field named "contents".
					// Specify a Reader, so that the text of the file is tokenized and indexed, but not stored.
					// Note that FileReader expects the file to be in UTF-8 encoding.
					// If that's not the case searching for special characters will fail.
					doc.add(new TextField("op_desc", new BufferedReader(new InputStreamReader(fis, "UTF-8"))));
                                        double boost = default_doc_boost;
                                        if (m_oConfigPopularities.containsKey(op_name))
                                        {
                                            boost = m_oConfigPopularities.get(op_name);
                                        }
                                        else if (m_oConfigPopularities.containsKey(op_name.toLowerCase()))
                                        {
                                            boost = m_oConfigPopularities.get(op_name.toLowerCase());
                                        }
                                        doc.add(new DoubleDocValuesField("boost", boost));
					if (writer.getConfig().getOpenMode() == IndexWriterConfig.OpenMode.CREATE) {
						// New index, so we just add the document (no old
						// document can be there):
						writer.addDocument(doc);
					} else {
						// Existing index (an old copy of this document may have been indexed)
						// so we use updateDocument instead to replace the old one matching the exact path, if present:
						System.out.println("updating " + file);
						writer.updateDocument(new Term("path", file.getPath()), doc);
					}
				} finally {
					fis.close();
				}
			}
		}
	}
	
        
        protected static void index_main(String index_path, String dst_dir, String popularity_file)
        {
            boolean create = true;
            new IndexFiles(popularity_file).indexDir(index_path, dst_dir, create);
        }
        
        protected static HashMap<String, String> parse_args(String[] args)
        {
            HashMap<String, String> res = new HashMap<>();
            CommandLineParser parser = new PosixParser();
            Options opts = new Options();
            opts.addOption(OptionBuilder.withArgName("index-path")
                    .hasArg()
                    .withDescription("indexing file's path")
                    .create("i"));
            opts.addOption(OptionBuilder.withArgName("dst-dir")
                    .hasArg()
                    .withDescription("destination file dir")
                    .create("d"));
            opts.addOption(OptionBuilder.withArgName("popularity-file")
                    .hasArg()
                    .withDescription("popularity file path")
                    .create("p"));
            try{
                CommandLine cmd = parser.parse(opts, args);
                if (cmd.hasOption("i"))
                {
                    res.put("index-path", cmd.getOptionValue("i"));
                }
                else
                {
                    System.out.println("index-path is required!");
                    HelpFormatter formatter = new HelpFormatter();
                    formatter.printHelp( "ant", opts );
                    System.exit(-1);
                }
                if (cmd.hasOption("d"))
                {
                    res.put("dst-dir", cmd.getOptionValue("d"));
                }
                else
                {
                    System.out.println("dst-dir is required!");
                    HelpFormatter formatter = new HelpFormatter();
                    formatter.printHelp( "ant", opts );
                    System.exit(-1);
                }
                if (cmd.hasOption("p"))
                {
                    res.put("popularity-file", cmd.getOptionValue("p"));
                }
                else{
                    res.put("popularity-file", null);
                }
            }
            catch(ParseException e)
            {
                System.out.println("unexpected exception in parse_args(): " + e.getLocalizedMessage());
            }
            
            return res;
        }
	/** Index all text files under a directory. */
	public static void main(String[] args) {
            /*String[] sargs = {"-d", 
                    "/Users/athrunarthur/xuepeng/icon/raw/httpd/", 
                    "-i", 
                    "/Users/athrunarthur/xuepeng/icon/index/httpd/",
                    "-p",
                    "/Users/athrunarthur/NetBeansProjects/iconfigure/data/n_mysql_popularity.txt"};
                    */
                log.setUseParentHandlers(false);
                try{
                    FileHandler fh = new FileHandler("index.log");
                    log.addHandler(fh);
                    SimpleFormatter formatter = new SimpleFormatter();  
                    fh.setFormatter(formatter);  
                }
                catch(Exception e)
                {
                    System.out.println("Unexpected exception : " + e.getMessage());
                }
                
                
                HashMap<String, String> params = parse_args(args);
                index_main(params.get("index-path"), params.get("dst-dir"), params.get("popularity-file"));

	}
}

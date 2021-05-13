import os
import glob
import ray
import fileinput
import time

class Analysis:
    
    def __init__(self, path, lib):
        '''
        The Init method creates the entire directory structure needed to perform the analysis. 
        Changing the directory names may result in execution errors.
        
        Arguments:
        path -- location of the folders containing the fastq file(s).
        lib -- 1 or more folders names.
        '''
        
        self.path = path
        self.lib = lib
        
        # checking the data type. If it is not a list, transform it
        if not isinstance(lib, list):
            aux = []
            aux.append(lib)
            lib = aux 
        
        try:
            os.chdir(path)
            print("Creating folders...")
            tic = time.time()
            for i in range(len(lib)):
                try:
                    os.mkdir(path +  '/' + lib[i] + '/Files_barcodes/')
                    print("Folder created with sucess!")
                except:
                    print("Folder needed for analysis already exist.")
                    pass
                try:
                    os.mkdir((path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_trim/'))
                    print("Folder created with sucess!")
                except:
                    print("Folder needed for analysis already exist.")
                    pass
                try:
                    os.mkdir((path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_alltrim/'))
                    print("Folder created with sucess!")
                except:
                    print("Folder needed for analysis already exist.")
                    pass
                try:
                    os.mkdir((path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_barcodes/'))
                    print("Folder created with sucess!")
                except:
                    print("Folder needed for analysis already exist.")
                    pass
                try:
                    os.mkdir((path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_filt/'))
                    print("Folder created with sucess!")
                except:
                    print("Folder needed for analysis already exist.")
                    pass 
                try:
                    os.mkdir((path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_minimap/'))
                    print("Folder created with sucess!")
                except:
                    print("Folder needed for analysis already exist.")
                    pass                    
                try:
                    os.mkdir((path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_minimap/tables'))
                    print("Folder created with sucess!")
                except:
                    print("Folder needed for analysis already exist.")
                    pass                
                tac = time.time()
                
        except KeyError:
            pass
        
        
        
    def merge_files(self, cpus):
        '''
        This method concatenates the demultiplexed files into a single file and moves it into the *_barcode folder.

        Arguments:
        cpus -- number of cpus;

        Returns:
        Concatenated files are moved to *_barcode folder.
        '''
        
        path = self.path
        lib = self.lib
        
        def concate_files(output_file):
            file_list = glob.glob("*.fastq")

            with open(output_file, 'w') as file:
                input_lines = fileinput.input(file_list)
                file.writelines(input_lines)

        # checking the data type. If it is not a list, transform it
        if not isinstance(lib, list):
            aux = []
            aux.append(lib)
            lib = aux
        
        for i in range(len(lib)):
            
            os.chdir(path + '/' + lib[i] + '/')
            
            barcodes_folders = sorted(os.listdir())
            
            # verify presence of unclassified files. If true remove its.
            if barcodes_folders.count('unclassified') > 0:
                barcodes_folders.remove('unclassified')
                
            barcodes_folders.remove('Files_barcodes')

            ray.init(num_cpus=cpus)

            # parallel method
            @ray.remote
            def concat(files):
                os.chdir(path + '/' + lib[i] + '/{0}/'.format(files))
                concate_files('{0}.fastq'.format(files))

            # putting files in the run list
            results = []
            for files in barcodes_folders:
                results.append(concat.remote(files))

            tic = time.time()
            ray.get(results) 
            tac = time.time()
            ray.shutdown()

            # moving concatenated files to *_barcodes/ folder
            for files in barcodes_folders:
                os.chdir(path + '/' + lib[i] + '/{0}/'.format(files))
                os.rename(path + '/' + lib[i] + '/{0}/{0}.fastq'.format(files), path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_barcodes/{0}.fastq'.format(files))

            print('Merged files are in folder: ' + path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_barcodes/.\nExecution time: ' + str(tac - tic) + ' s\n')
    
    
    def guppy_barcoder(self, cpus, barcode_kits = None):
        
        '''
        This method receives executes the commands from the guppy_barcoder software  and executes them.
        
        Arguments:
        cpus -- number of CPUs for execution. Integer;
        barcodes_kits -- specification of the barcode kit used by sequencing. If not specified, the method considers the default sequencing barcode kit. str.
        
        Returns:
        This method adds in the *_trim folder the results of the guppy_barcoder run.
        '''
        
        path = self.path
        lib = self.lib

        # checking the data type. If it is not a list, transform it
        if not isinstance(lib, list):
            aux = []
            aux.append(lib)
            lib = aux
            
        # iterating on samples to be analyzed    
        for i in range(len(lib)):
            if barcode_kits:
                print("Starting the trimming of files from " + lib[i] + "_trim/ folder...")
                tic = time.time()
                command = 'guppy_barcoder -i ' + path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_barcodes/ -s' + path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_trim/ --barcode_kits ' + barcode_kits + ' --trim_barcodes -t ' + str(cpus)
                os.system(command)
                tac = time.time()
                
                print("Completed.\nExecution time: " + str(tac - tic) + " s")
            else:
                print("Starting the trimming of files from " + lib[i] + "_trim/ folder...") 
                tic = time.time()
                command = 'guppy_barcoder -i ' + path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_barcodes/ -s' + path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_trim/  --trim_barcodes -t ' + str(cpus)
                os.system(command)
                tac = time.time()
                
                print("Completed.\nExecution time: " + str(tac - tic) + " s") 
                
            print('Barcoded trimmed files are in the ' + path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_trim/ folder.')
    
    
    def nanofilt(self, cpus, q = 10, l = 1350, maxlength = 1650, just_filt = False):
        '''
        This method takes some arguments from the NanoFilt software and executes them in parallel. Each file can be filtered in a separate core.

        Arguments:
        q -- integer representing the quality score of the sequence.
        l -- integer representing the sequence length
        maxlenght -- maximum sequence length
        just_filt -- boolean. If true, the method will only filter the data. Note that for this, the concatenated files must already be in the *_alltrim folder.
        
        Returns:
        This method add all filered files in *_filt folder.

        For more information, see https://github.com/wdecoster/nanofilt.
        '''
        
        path = self.path
        lib = self.lib
        self.q = q
        
        def concate_files(output_file):
            file_list = glob.glob("*.fastq")

            with open(output_file, 'w') as file:
                input_lines = fileinput.input(file_list)
                file.writelines(input_lines)
                
        # concate files
        def init_concate_files():
            ray.init(num_cpus=cpus)
            
            # parallel method
            @ray.remote
            def concat(folders):
                os.chdir(path + '/'+ lib[i] + '/Files_barcodes/' + lib[i] + '_trim/{0}/'.format(folders))
                concate_files('{0}_trim.fastq'.format(folders))
    
            results = []
            for folders in barcodes_folders:
                results.append(concat.remote(folders))
                
            ray.get(results) 
        
            
        # nanofilt quality control
        def init_nanofilt():
            
            ray.init(num_cpus = cpus)
            
            # parallel method
            @ray.remote
            def filt(files):
                command = ('NanoFilt -q ' + str(q) +' -l ' + str(l) +' --maxlength ' + str(maxlength) + ' ' + files +  ' > ' + path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_filt/{0}_filt_q'.format(files) + str(q) +'.fastq')
                os.system(command)

            results = []
            for files in trim_files:
                results.append(filt.remote(files))

            ray.get(results)
            
        
        # checking the data type. If it is not a list, transform it
        if not isinstance(lib, list):
            aux = []
            aux.append(lib)
            lib = aux
        
        for i in range(len(lib)):
            if not just_filt:
                print("Starting file concatenation from " + lib[i] + "_trim/ folder...\n")
                os.chdir(path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_trim/')
                barcodes_folders = sorted(os.listdir())
                drop = glob.glob("*.*")

                for d in range(len(drop)):
                    barcodes_folders.remove(drop[d])

                # verify presence of unclassified files. If true remove its.
                if barcodes_folders.count('unclassified') > 0:
                    barcodes_folders.remove('unclassified')
                                                
                # init parallel mode    
                try:
                    tic = time.time()
                    init_concate_files()
                    tac = time.time()
                except:
                    ray.shutdown()
                    tic = time.time()
                    init_concate_files()
                    tac = time.time()
                ray.shutdown()

                print("Started move files from /" + lib[i] + "_trim folder to /" + lib[i] + "_alltrim folder...\n")
                for folders in barcodes_folders:
                    os.chdir(path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_trim/{0}/'.format(folders))
                    #print("first ", path + '/'+ lib[i] + '/Files_barcodes/' + lib[i] + '_trim/{0}/'.format(folders))
                    os.rename(path + '/' + lib[i] + '/Files_barcodes/'+ lib[i] + '_trim/{0}/{0}_trim.fastq'.format(folders), path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_alltrim/{0}_trim.fastq'.format(folders))

                print('Trimmed barcodes files are in ' + path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_alltrim/\nExecution time: ' + str(tac - tic) + ' s\n')

                
            os.chdir(path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_alltrim/')
            trim_files = sorted(os.listdir())
            print("Filtering ", len(trim_files) , "files in folder /" + lib[i] + '_alltrim...\n')


            print("Started filtering files from /" + lib[i] + "_alltrim/ folder...\n")
            
            try:
                # nanofilt quality control
                tic = time.time()
                init_nanofilt()
                tac =time.time()
            except:
                ray.shutdown()
                # nanofilt quality control
                tic = time.time()
                init_nanofilt()
                tac =time.time()
                
            ray.shutdown()

            print("Filtered files are in " + path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_filt/\nExecution time: ' + str(tac - tic) + ' s\n')


    def minimap(self, cpus, refseqpath, nanofilt_q, refseq = 'refseq_16S.fa'):
        '''
        This method receives some arguments from the minimap2 software. Parallelized method with ray library.

        Arguments:
        refseqpath -- string with location of the reference database.
        nanofilt_q -- integer with quality score used in the quality control step with NanoFilt.
        refseq -- string name of the reference sequence file.
        
        '''
        
        path = self.path
        lib = self.lib
    
        def init_minimap():
            
            ray.init(num_cpus = cpus)

            # parallel method
            @ray.remote
            def filt(files):
                command = ('minimap2 -cx map-ont ' + refseqpath + '/ncbi/' + refseq + ' {0}'.format(files) + ' > ' + path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_minimap/{0}_align'.format(files.replace('_trim.fastq_filt'+ str(nanofilt_q) + '.fastq', 'q'+ str(nanofilt_q))))
                os.system(command)

            results = []
            for files in filt_files:
                results.append(filt.remote(files))

            tic = time.time()
            ray.get(results)
            tac = time.time()
            
        # checking the data type. If it is not a list, transform it    
        if not isinstance(lib, list):
            aux = []
            aux.append(lib)
            lib = aux 
        
        for i in range(len(lib)):
            os.chdir(path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_filt/')
            filt_files = glob.glob('*.fastq')
            filt_files = sorted(filt_files)
            
            try:
                tic = time.time()
                # minimap align
                init_minimap()
                tac = time.time()
            except:
                ray.shutdown()
                tic = time.time()
                # minimap align
                init_minimap()
                tac = time.time()
                
            ray.shutdown()
            
            print("Aligned files are in " + path + '/' + lib[i] + '/Files_barcodes/' + lib[i] + '_minimap/\nExecution time: ' + str(tac - tic) + ' s\n')
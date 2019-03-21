#https://developer.basespace.illumina.com/docs/content/documentation/native-apps/spacedock-conventions#UploadResultstoBaseSpacewithProperties

import glob, json, os, subprocess, sys

#manage some large files
#reference fasta is too large for github; thus it's stored in the base image as a compressed file to save space, but this means it must be 
#de-compressed before use; to avoid doing this in every cromwell-spawned child container, decompress here then mount it in the child containers
#vep cache is too large to even store in the image, so download it once here in the base container then mount in child containers
os.chdir('/persist')

#decompress reference fasta file
print('Decompressing reference fasta...')
subprocess.check_call(['gunzip', 'all_sequences.fa.gz'])
print('Done decompressing')

#download and setup VEP cache
print('Downloading VEP cache, this may take a while...')
subprocess.check_call(['curl', '-OsS', 'ftp://ftp.ensembl.org/pub/release-90/variation/VEP/homo_sapiens_vep_90_GRCh38.tar.gz'])
print('Download complete. Unpacking...')
subprocess.check_call(['tar', 'xzf', 'homo_sapiens_vep_90_GRCh38.tar.gz'])
print('Unpacking complete')


#get basespace related properties/metadata
with open("/data/input/AppSession.json") as a_s_j:
    appsession = json.load(a_s_j)

#finding the ID of the project from which this analysis was launched; this is needed in order
#to create the directory structure specified by basespace for automatic result uploading
for e in appsession['Properties']['Items']:
    if e['Name'] == 'Input.Projects':
        project_id = e['Items'][0]['Id'] #note that this will return a unicode object, not a str; this is still python 2.7.x, so these are 2 different things
    if e['Name'] == 'Input.Files':
        file_href = e['Items'][0]['Href'] #note that this is a hardcoded example; there may be multiple requiring more complex logic in production
appsession_href = appsession['Href'] #basespace internal reference to the current appsession

cram_search = glob.glob('/data/input/appresults/*/*.cram')
if len(cram_search) != 1:
    print('Error- expected 1 cram file but found {0}'.format(len(cram_search)))
    sys.exit(1)
crai_search = glob.glob('/data/input/appresults/*/*.crai')
if len(crai_search) != 1:
    print('Error- expected 1 crai file but found {0}'.format(len(cram_search)))
    sys.exit(1)

cram_file = cram_search[0]
crai_file = crai_search[0]
name = cram_file.split("/")[-1].split(".")[0]

#basespace-specified directory structure: /data/output/appresults/<project-id>/[directory_with_appresult_name]/[your_files]
output_dir = "/data/output/appresults/{0}/{1}".format(project_id, name) 
os.makedirs(output_dir) #recursively create the output directory

#create inputs.json file
wf_inputs_dict = \
{
    "ChromoSeq.Cram": cram_file,
    "ChromoSeq.CramIndex": crai_file,
    "ChromoSeq.Name": name,
    "ChromoSeq.OutputDir": output_dir
}

with open("/opt/inputs.json", "w+") as f:
    json.dump(wf_inputs_dict, f)

#create metadata file required by basespace for upload; each workflow generated ouput file is tagged
#with the downloaded basespace file(s) used to generate it

metadata_outfile = output_dir + "/_metadata.json"

#note that the value of key "Name" must match the dirname at the trailing end of $output_dir
metadata_json_template = \
{
    "Name": name,
    "Description": "Outputs from Chromoseq workflow run on {}".format(cram_file),
    "HrefAppSession": appsession_href,
    "Properties": [
        {
            "Type": "file[]",
            "Name": "Input.Files",
            "Items": [
            
		]
        }
    ]
}
metadata_json_template['Properties'][0]['Items'].append(file_href) #TODO should all files be included here? if not this line can be deleted and assignment placed inline

with open(metadata_outfile, "w+") as f:
    json.dump(metadata_json_template, f)

print('\nLaunching cromwell')
cromwell_cmd = ["/usr/bin/java", "-Dconfig.file=/opt/basespace_cromwell.config", "-jar", "/opt/cromwell-36.jar", "run", "-t", "wdl", "-i", "/opt/inputs.json", "/opt/Chromoseq.v8.cromwell34.hg38.wdl"]
subprocess.check_call(cromwell_cmd)
print('\nCromwell complete')

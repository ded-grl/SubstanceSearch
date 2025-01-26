import fetch from 'node-fetch';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const otherData = JSON.parse(fs.readFileSync('data/final_updated_drugs.json'));

const outputFile = 'data/raw_psychonaut.json';

async function querySubstance(substanceName) {
    console.log(`Querying PsychonautWiki API for: ${substanceName}`);
    
    const query = `{
        substances(query: "${substanceName}") {
            name
            roas {
                name
                dose {
                    units
                    threshold
                    heavy
                    common { min max }
                    light { min max }
                    strong { min max }
                }
                duration {
                    afterglow { min max units }
                    comeup { min max units }
                    duration { min max units }
                    offset { min max units }
                    onset { min max units }
                    peak { min max units }
                    total { min max units }
                }
                bioavailability {
                    min max
                }
            }
            effects {
                name
                url
            }
        }
    }`;

    try {
        const response = await fetch('https://api.psychonautwiki.org/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
        });
        
        const data = await response.json();
        console.log(`✓ Successfully retrieved data for: ${substanceName}`);
        return data;
    } catch (error) {
        console.error(`✗ Error querying data for ${substanceName}:`, error);
        return null;
    }
}

const fetchedData = {};

console.log(`Starting to process ${Object.keys(otherData).length} substances...`);
let processed = 0;

for (const substanceName in otherData) {
    const queriedData = await querySubstance(substanceName);
    
    if (queriedData) {
        fetchedData[substanceName] = queriedData;
        processed++;
        console.log(`Progress: ${processed}/${Object.keys(otherData).length} substances processed`);
    }
}

console.log('Writing data to output file...');
fs.writeFileSync(outputFile, JSON.stringify(fetchedData, null, 4));

console.log('✓ Data queried and saved successfully to', outputFile);
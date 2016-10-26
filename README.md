This project supports the article [http://www.kdgregory.com/index.php?page=maven.s3Deploy].
It contains the following components, which are described in detail below:

* `AWS`: configuration for AWS; sub-directories are named after the AWS service.
* `Deployed-Project`: a simple Maven project that will be deployed to S3.
* `Consuming-Project`: a simple Maven project that depends on the previous project.
* `settings.xml`: example Maven settings to read from a repository server. This is adapted from the Nexus
  Repository Manager [documentation](http://books.sonatype.com/nexus-book/reference/config-maven.html).
* `scripts`: some utility scripts to configure projects for those following along at home
  (these are all Linux bash scripts; if you don't use Linux you're on your own).


## Building the sample projects

Prerequisites:

* You've configured AWS and Nexus as described [in the article](http://www.kdgregory.com/index.php?page=maven.s3Deploy).
  You can find example policy documents and the Lambda source code in the `AWS`
  sub-directory, but you'll need to change any references to `example.com` to
  your own domain.
* A JDK (not JRE!). The version shouldn't matter; on Ubuntu I install `openjdk-7-jdk`.
* A recent version of Maven. At this time Ubuntu installs 3.0.5, which is rather
  old; you can download the latest version from [maven.apache.org](http://maven.apache.org/download.cgi).

Now for the manual steps to do in this directory:

1. Remove the `.git` directory from this working directory. It's not needed (you won't be checking
stuff back in), and sometimes Git gets confused when it has nested repositories. Since this is a
destructive action, I want you to do it explicitly.
2. Edit the file `settings.xml` to change the repository URL, and move it into `$HOME/.m2` (after
backing-up any existing settings file that you might have!).
3. Change the `distributionManagement` section of `Deployed-Project/pom.xml` to point to your own
bucket. Your releases will fail if you leave it pointing at mine.
4. Run the script `scripts/setup-projects.sh`, which moves the directory `Deployed-Project` to `/tmp`,
turns it into a Git "remote" repository, and clones it back to the project directory. This is necessary
for the Maven release plugin to work.

Now you're ready to run `mvn release` on `Deployed_Project`. You should see the files being uploaded to S3.

And assuming that your Nexus server is up and running, you should be able to run `mvn test` in
`Consuming-Project`, and see it download the snapshot from Nexus.

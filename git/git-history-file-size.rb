# Displays size of file in Git repository at each commit.
# 
# Run from Git repository root with file as argument.
#
# [code taken from http://stackoverflow.com/a/3151300/390441]
require 'rubygems'
require 'grit'

if ARGV.size < 1
	puts 'usage: file-size FILE'
	puts 'run from within the git repo root'
	exit
end

filename = ARGV[0].to_s

repo = Grit::Repo.new('.')
commits = repo.log('master', filename)
commits.each do |commit|
	blob = commit.tree/filename
	puts "#{commit} #{blob.size} bytes"
end

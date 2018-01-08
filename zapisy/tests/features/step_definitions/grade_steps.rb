# encoding: utf-8
require 'uri'
require 'cgi'

def run_client(input_file)
    path = "../static/Downloads/"
    system "rm -rf tickets.txt"
    system "python #{path}client.py < client_input/#{input_file} > out"
    system "rm -rf out"
end

When /^I uncheck "([^"]*)" checkboxes in tickets grouping options$/ do |arg|
	if arg == "all" then
		# both checkboxes to uncheck
		uncheck("join_1")
		uncheck("join_2")		
	elsif arg == "some" then
		# first checkbox to uncheck	
		uncheck("join_1")
	elsif arg == "no" then
		# we do not touch anything then
	end
end

When /^I run client with "([^"]*)"$/ do |file|
    run_client( file )
end

Then /^tickets should not be connected$/ do
    ticket_client = ""
    file   = File.new("tickets.txt", "r")
    for i in 1..4:
        ticket_client = file.gets
    end
    file.close
    ticket_fereol = page.find(:xpath, "//*[textarea[(@id='keys')]]").text.split( "id: 5" )[1].split( " " )[ 0 ]
    ticket_client.should_not be_eql( ticket_fereol )
end

Then /^tickets file should not exist$/ do
    file_list = Dir.glob("*.txt")
    file_list.should_not be_include( "tickets.txt" )
end

When /^I enter generated ticket$/ do
    ticket_client = ""
    file   = File.new("tickets.txt", "r")
    while( line = file.gets )
        ticket_client += line
    end
    file.close
    fill_in("Podaj wygenerowane bilety:", :with => ticket_client)
end

When /^I delete "([^"]*)" section$/ do |name|
	page.find(:xpath, "//*[text()=\"#{name}\"]/following-sibling::*[@alt=\"usuń\"]").click()
end

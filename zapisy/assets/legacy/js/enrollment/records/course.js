/**
 * Model kursu (przedmiotu) - przechowuje dane.
 */

if (!Fereol.Enrollment)
	Fereol.Enrollment = new Object();

Fereol.Enrollment.Course = function()
{
	this.id = null;
	this.type = null;
	this.name = null;
	this.shortName = null;
	this.url = null;
	this.isRecordingOpen = null;
};

Fereol.Enrollment.Course._byID = {};

Fereol.Enrollment.Course.prototype._register = function()
{
	Fereol.Enrollment.Course._byID[this.id] = this;
};

Fereol.Enrollment.Course.getByID = function(id)
{
	if (!Fereol.Enrollment.Course._byID[id])
		throw new Error('Kurs nie istnieje');
	return Fereol.Enrollment.Course._byID[id];
};

Fereol.Enrollment.Course.fromJSON = function(json)
{
	var raw = json;
	if (typeof raw == 'string')
		raw = $.parseJSON(json);

	var c = new Fereol.Enrollment.Course();

	c.id = raw['id'].castToInt();
	c.type = raw['type'].castToInt();
	c.name = raw['name'];
	c.shortName = raw['short_name'];
	c.url = raw['url'];
	c.isRecordingOpen = !!raw['is_recording_open'];

	c._register();
	return c;
};

Fereol.Enrollment.Course.prototype.toString = function()
{
	return 'Course#' + this.id + ':' + this.name;
}

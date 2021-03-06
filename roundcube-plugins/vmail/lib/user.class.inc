<?php

require_once 'base.class.inc';

class User extends Base
{
	public $keys = array(
		'domain_id', 'email', 'secondary_email', 'name', 'password',
		'cleartext', 'quota', 'usage', 'enabled', 'admin');
	
	public function __get($key)
	{
		if (!array_key_exists($key, $this->cache)) {
			switch ($key) {
				case 'domain':
					$this->cache['domain'] = Domain::get_domain($this->domain_id);
					break;

				case 'forward':
					$this->cache['forward'] = Forward::get_forward($this->email);
					break;

				case 'forwarding':
					$forward = $this->forward;
					$destinations = $this->forward->destinations;

					if (count($destinations) == 0) {
						$this->cache['forwarding'] = 'std';
						$this->cache['savecopy'] = false;
						break;
					}

					$index = array_search($this->email, $destinations);
					if ($index !== false && count($destinations) >= 2) {
						unset($destinations[$index]);
						$this->cache['savecopy'] = true;
						$this->cache['forwarding'] = 'fwd';
					} else if (count($destinations) >= 1) {
						$this->cache['savecopy'] = false;
						$this->cache['forwarding'] = 'fwd';
					}

					$forward->destinations = $destinations;
					break;

				case 'vacation':
					$this->cache['vacation'] = Vacation::get_vacation($this->email);
					break;
			}
		}
		return parent::__get($key);
	}

	public function fget($key)
	{
		if ($key == 'quota' || $key == 'usage') {
			return show_bytes($this->data[$key]);
		} else if ($key == 'enabled') {
			return ($this->data[$key]) ? $this->gettext('yes') : $this->gettext('no');
		} else {
			return $this->data[$key];
		}
	}

	public function delete()
	{
		$this->client->core->delete_user($this->id);
	}

	public function save()
	{
		$params = $this->get_params();
		if (count($params) == 0) return;
		$result = $this->client->core->save_user($this->id, $params);
		if ($result > 0) $this->id = $result;
	}
	
	/********************
	 * Static functions *
	 ********************/
	public static function get_user($username)
	{
		$user = new User();
		$data = $user->client->core->get_user($username);
		$user->load($data);
		return $user;
	}

	public static function from_data($data)
	{
		$user = new User();
		$user->load($data);
		return $user;
	}
}
?>

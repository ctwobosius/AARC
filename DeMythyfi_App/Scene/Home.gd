extends Control

func _ready() -> void:
#	modulate.a = 0
	$Body/SearchBar/Margin/TextEdit.text = G.searched
	if get_node_or_null("Anim"):
		$Anim.play("Fade")
	var stocks := get_node_or_null("Body/TabContainer/Stocks/Stonks")
	if stocks:
		for child in stocks.get_children():
			if child is Topic:
				child._on_Toggle_button_down()





func _on_SearchBar_searched():
	if get_node_or_null("Anim"):
		$Anim.play_backwards("Fade")
		yield($Anim, "animation_finished")
	get_tree().change_scene("res://Scene/SearchResults.tscn")
